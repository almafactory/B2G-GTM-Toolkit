from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from b2g_gtm_toolkit.models.secop import (
    SecopNormalizedRecord,
    SecopResearchInput,
)
from b2g_gtm_toolkit.secop.client import SocrataClient, build_where_clause
from b2g_gtm_toolkit.secop.datasets import DATASETS, DatasetSpec, get_dataset
from b2g_gtm_toolkit.secop.dedupe import dedupe
from b2g_gtm_toolkit.secop.normalize import normalize_record
from b2g_gtm_toolkit.utils.ids import now_utc, stable_id
from b2g_gtm_toolkit.utils.logging import get_logger


_LOG = get_logger(__name__)


RecordSource = Callable[[DatasetSpec, SecopResearchInput], Iterable[Dict[str, Any]]]


SCHEMA_RECORD_FIELDS = {
    "source_platform",
    "source_dataset",
    "source_record_id",
    "source_url",
    "process_id",
    "contract_id",
    "buyer_name",
    "buyer_nit",
    "supplier_name",
    "supplier_nit",
    "object",
    "modality",
    "status",
    "contract_value",
    "currency",
    "publication_date",
    "award_date",
    "deadline",
    "unspsc_codes",
    "matched_account_id",
    "relevance",
    "provenance",
}

PROVENANCE_SCHEMA_FIELDS = {"retrieved_at", "query", "raw_payload_hash"}


@dataclass
class ResearchRun:
    run_id: str
    run_dir: Path
    jsonl_path: Path
    manifest_path: Path
    raw_count: int
    deduped_count: int
    datasets: List[str]
    started_at: datetime
    finished_at: datetime


def _selected_datasets(input_data: SecopResearchInput) -> List[DatasetSpec]:
    requested = input_data.datasets or ["secop_ii_procesos", "secop_ii_contratos"]
    specs: List[DatasetSpec] = []
    for name in requested:
        try:
            specs.append(get_dataset(name))
        except KeyError:
            _LOG.warning("secop.research.unknown_dataset", extra={"dataset": name})
    if not specs:
        specs = [DATASETS["secop_ii_procesos"]]
    return specs


def _input_filters_to_where(input_data: SecopResearchInput, dataset: DatasetSpec) -> Optional[str]:
    filters: Dict[str, Any] = {}
    if input_data.entity_nits:
        for raw_key, normalized in dataset.field_map.items():
            if normalized == "buyer_nit":
                filters[raw_key] = input_data.entity_nits
                break
    clauses = []
    exact_clause = build_where_clause(filters)
    if exact_clause:
        clauses.append(exact_clause)

    field_by_normalized = {normalized: raw_key for raw_key, normalized in dataset.field_map.items()}
    contains_specs = [
        ("buyer_name", input_data.entity_names),
        ("municipality", input_data.municipalities),
        ("department", input_data.departments),
        ("object", input_data.keywords),
        ("unspsc_primary", input_data.unspsc_codes),
        ("modality", input_data.modalities),
        ("status", input_data.statuses),
        ("supplier_name", input_data.suppliers),
    ]
    for normalized_field, values in contains_specs:
        raw_key = field_by_normalized.get(normalized_field)
        if raw_key:
            clause = _contains_any_clause(raw_key, values)
            if clause:
                clauses.append(clause)

    if not clauses:
        return None
    return " AND ".join(f"({clause})" for clause in clauses)


def _contains_any_clause(field: str, values: List[str]) -> Optional[str]:
    cleaned = [value.strip() for value in values if value and value.strip()]
    if not cleaned:
        return None
    parts = []
    for value in cleaned:
        variants = {value, value.upper(), value.title()}
        for variant in variants:
            safe = variant.replace("'", "''")
            parts.append(f"{field} like '%{safe}%'")
    return " OR ".join(parts)


def _default_record_source(client: Optional[SocrataClient]) -> RecordSource:
    owns = client is None

    def source(dataset: DatasetSpec, input_data: SecopResearchInput) -> Iterable[Dict[str, Any]]:
        c = client or SocrataClient()
        try:
            where = _input_filters_to_where(input_data, dataset)
            yield from c.iter_records(
                dataset,
                where=where,
                page_size=input_data.page_size,
                max_records=input_data.result_limit,
            )
        finally:
            if owns:
                c.close()

    return source


def _make_run_id(input_data: SecopResearchInput) -> str:
    timestamp = now_utc().strftime("%Y%m%d-%H%M%S")
    slug_parts: List[str] = [input_data.task_type.value]
    slug_parts.extend(input_data.entity_nits[:1])
    slug_parts.extend(input_data.entity_names[:1])
    slug_parts.extend(input_data.keywords[:1])
    slug = stable_id(*slug_parts) if slug_parts else stable_id(input_data.task_type.value)
    return f"{timestamp}-{slug}"


_NULLABLE_FIELDS = {
    "source_url",
    "process_id",
    "contract_id",
    "buyer_nit",
    "supplier_name",
    "supplier_nit",
    "modality",
    "status",
    "contract_value",
    "publication_date",
    "award_date",
    "deadline",
    "matched_account_id",
}


def _record_to_schema_dict(record: SecopNormalizedRecord) -> Dict[str, Any]:
    raw = record.model_dump(mode="json")
    out: Dict[str, Any] = {}
    for key in SCHEMA_RECORD_FIELDS:
        if key not in raw:
            continue
        value = raw[key]
        if value is None and key not in _NULLABLE_FIELDS:
            continue
        out[key] = value
    prov = raw.get("provenance") or {}
    out["provenance"] = {k: prov[k] for k in PROVENANCE_SCHEMA_FIELDS if k in prov}
    if "currency" not in out or out["currency"] is None:
        out["currency"] = "COP"
    if "unspsc_codes" not in out or out["unspsc_codes"] is None:
        out["unspsc_codes"] = []
    return out


def run_research(
    input_data: SecopResearchInput,
    output_root: Optional[Path] = None,
    record_source: Optional[RecordSource] = None,
    offline_fixtures: Optional[Dict[str, Path]] = None,
) -> ResearchRun:
    started_at = now_utc()
    run_id = _make_run_id(input_data)
    base = output_root or Path("data/runs")
    run_dir = base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = run_dir / "secop-research.jsonl"
    manifest_path = run_dir / "manifest.json"

    datasets = _selected_datasets(input_data)

    if offline_fixtures is not None:
        record_source = _fixture_record_source(offline_fixtures)
    if record_source is None:
        record_source = _default_record_source(client=None)

    raw_count = 0
    normalized: List[SecopNormalizedRecord] = []
    query_dict = input_data.model_dump(mode="json", exclude_none=True)
    for dataset in datasets:
        _LOG.info(
            "secop.research.dataset.start",
            extra={"dataset": dataset.name, "id": dataset.dataset_id},
        )
        for raw in record_source(dataset, input_data):
            raw_count += 1
            normalized.append(normalize_record(raw, dataset, query=query_dict))

    deduped = dedupe(normalized)

    with jsonl_path.open("w", encoding="utf-8") as fh:
        for rec in deduped:
            fh.write(json.dumps(_record_to_schema_dict(rec), ensure_ascii=False, default=str))
            fh.write("\n")

    finished_at = now_utc()
    manifest = {
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "datasets": [d.name for d in datasets],
        "dataset_ids": [d.dataset_id for d in datasets],
        "raw_count": raw_count,
        "deduped_count": len(deduped),
        "input": query_dict,
        "output": {
            "jsonl": str(jsonl_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    return ResearchRun(
        run_id=run_id,
        run_dir=run_dir,
        jsonl_path=jsonl_path,
        manifest_path=manifest_path,
        raw_count=raw_count,
        deduped_count=len(deduped),
        datasets=[d.name for d in datasets],
        started_at=started_at,
        finished_at=finished_at,
    )


def _fixture_record_source(fixtures: Dict[str, Path]) -> RecordSource:
    def source(dataset: DatasetSpec, input_data: SecopResearchInput) -> Iterable[Dict[str, Any]]:
        path = fixtures.get(dataset.name)
        if path is None:
            return []
        if not path.exists():
            _LOG.warning("secop.research.fixture_missing", extra={"path": str(path)})
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("records", [])
        limit = input_data.result_limit
        return list(data)[:limit]

    return source


def default_offline_fixtures(base_dir: Optional[Path] = None) -> Dict[str, Path]:
    base = base_dir or Path("tests/fixtures/secop")
    return {
        "secop_ii_procesos": base / "secop_ii_procesos.sample.json",
        "secop_ii_contratos": base / "secop_ii_contratos.sample.json",
        "secop_i_procesos": base / "secop_i_procesos.sample.json",
    }
