from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional

from b2g_gtm_toolkit.models.secop import (
    Provenance,
    SecopNormalizedRecord,
)
from b2g_gtm_toolkit.secop.datasets import DatasetSpec
from b2g_gtm_toolkit.utils.ids import hash_payload, now_utc


_CURRENCY_RE = re.compile(r"[^0-9.\-]")


def parse_currency(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    sign = -1.0 if text.startswith("-") else 1.0
    digits = re.sub(r"[^0-9.,]", "", text)
    if not digits:
        return None
    last_dot = digits.rfind(".")
    last_comma = digits.rfind(",")
    if last_dot == -1 and last_comma == -1:
        cleaned = digits
    elif last_comma > last_dot:
        cleaned = digits.replace(".", "").replace(",", ".")
    else:
        cleaned = digits.replace(",", "")
        if cleaned.count(".") > 1:
            cleaned = cleaned.replace(".", "")
    if cleaned in ("", "-", "."):
        return None
    try:
        return sign * float(cleaned)
    except ValueError:
        return None


def parse_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _apply_field_map(raw: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for raw_key, normalized_key in field_map.items():
        if raw_key in raw and raw[raw_key] not in (None, ""):
            out[normalized_key] = raw[raw_key]
    return out


def _coerce_source_url(value: Any) -> Optional[str]:
    """Socrata a veces devuelve urlproceso como string y a veces como objeto {\"url\": \"...\"}."""
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, dict):
        for key in ("url", "href", "link"):
            inner = value.get(key)
            if isinstance(inner, str) and inner.strip():
                return inner.strip()
    return None


def _build_source_record_id(dataset: DatasetSpec, mapped: Dict[str, Any], raw: Dict[str, Any]) -> str:
    candidate = (
        mapped.get("contract_id")
        or mapped.get("process_id")
        or raw.get("id")
        or raw.get(":id")
    )
    if candidate:
        return str(candidate)
    return hash_payload(raw)[:16]


def normalize_record(
    raw: Dict[str, Any],
    dataset: DatasetSpec,
    query: Optional[Dict[str, Any]] = None,
    retrieved_at: Optional[datetime] = None,
) -> SecopNormalizedRecord:
    mapped = _apply_field_map(raw, dataset.field_map)

    buyer_name = mapped.get("buyer_name") or "(sin nombre de comprador)"
    obj = mapped.get("object") or "(sin objeto)"

    contract_value = parse_currency(mapped.get("contract_value"))
    publication_date = parse_date(mapped.get("publication_date"))
    award_date = parse_date(mapped.get("award_date"))
    start_date = parse_date(mapped.get("start_date"))
    end_date = parse_date(mapped.get("end_date"))
    deadline = parse_datetime(mapped.get("deadline"))

    unspsc_codes: list[str] = []
    primary = mapped.get("unspsc_primary")
    if primary:
        unspsc_codes.append(str(primary))

    source_url = _coerce_source_url(mapped.get("source_url"))

    provenance = Provenance(
        source_dataset=dataset.dataset_id,
        source_url=source_url,
        retrieved_at=retrieved_at or now_utc(),
        raw_payload_hash=hash_payload(raw),
        query=query or {},
    )

    return SecopNormalizedRecord(
        source_platform=dataset.source_platform,
        source_dataset=dataset.dataset_id,
        source_record_id=_build_source_record_id(dataset, mapped, raw),
        source_url=source_url,
        process_id=mapped.get("process_id"),
        contract_id=mapped.get("contract_id"),
        buyer_name=buyer_name,
        buyer_nit=mapped.get("buyer_nit"),
        supplier_name=mapped.get("supplier_name"),
        supplier_nit=mapped.get("supplier_nit"),
        object=obj,
        modality=mapped.get("modality"),
        status=mapped.get("status"),
        contract_value=contract_value,
        currency="COP",
        publication_date=publication_date,
        award_date=award_date,
        start_date=start_date,
        end_date=end_date,
        deadline=deadline,
        unspsc_codes=unspsc_codes,
        provenance=provenance,
    )
