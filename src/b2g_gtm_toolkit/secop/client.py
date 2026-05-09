from __future__ import annotations

import os
from typing import Any, Dict, Iterator, Optional

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from b2g_gtm_toolkit.secop.datasets import DatasetSpec
from b2g_gtm_toolkit.utils.logging import get_logger


_LOG = get_logger(__name__)


class SocrataClient:
    def __init__(
        self,
        timeout: float = 30.0,
        app_token: Optional[str] = None,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self._app_token = app_token or os.environ.get("DATOS_GOV_APP_TOKEN")
        headers = {"Accept": "application/json"}
        if self._app_token:
            headers["X-App-Token"] = self._app_token
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout, headers=headers)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "SocrataClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @retry(
        reraise=True,
        retry=retry_if_exception_type((httpx.HTTPError,)),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def _get(self, url: str, params: Dict[str, Any]) -> list[dict]:
        response = self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def iter_records(
        self,
        dataset: DatasetSpec,
        where: Optional[str] = None,
        page_size: int = 200,
        max_records: int = 1000,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        offset = 0
        fetched = 0
        url = dataset.endpoint
        while fetched < max_records:
            limit = min(page_size, max_records - fetched)
            params: Dict[str, Any] = {"$limit": limit, "$offset": offset}
            if where:
                params["$where"] = where
            if extra_params:
                params.update(extra_params)
            _LOG.info(
                "secop.client.fetch",
                extra={"dataset": dataset.name, "offset": offset, "limit": limit},
            )
            batch = self._get(url, params)
            if not batch:
                break
            for record in batch:
                yield record
                fetched += 1
                if fetched >= max_records:
                    break
            if len(batch) < limit:
                break
            offset += len(batch)


def build_where_clause(filters: Dict[str, Any]) -> Optional[str]:
    parts: list[str] = []
    for key, value in filters.items():
        if value is None:
            continue
        if isinstance(value, list):
            if not value:
                continue
            quoted = ", ".join(f"'{str(v).replace("'", "''")}'" for v in value)
            parts.append(f"{key} IN ({quoted})")
        elif isinstance(value, (int, float)):
            parts.append(f"{key} = {value}")
        else:
            safe = str(value).replace("'", "''")
            parts.append(f"{key} = '{safe}'")
    if not parts:
        return None
    return " AND ".join(parts)
