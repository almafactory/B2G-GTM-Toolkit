from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from b2g_gtm_toolkit.models.secop import SecopNormalizedRecord
from b2g_gtm_toolkit.utils.ids import normalize_text


def _primary_key(record: SecopNormalizedRecord) -> Tuple[str, ...]:
    if record.contract_id:
        return ("contract", record.source_dataset, record.contract_id)
    if record.process_id:
        return ("process", record.source_dataset, record.process_id)
    year = record.publication_date.year if record.publication_date else 0
    return (
        "fallback",
        record.buyer_nit or normalize_text(record.buyer_name),
        normalize_text(record.object)[:120],
        str(record.contract_value or 0),
        str(year),
    )


def dedupe(records: Iterable[SecopNormalizedRecord]) -> List[SecopNormalizedRecord]:
    by_key: Dict[Tuple[str, ...], SecopNormalizedRecord] = {}
    for rec in records:
        key = _primary_key(rec)
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = rec
            continue
        if rec.provenance.retrieved_at >= existing.provenance.retrieved_at:
            by_key[key] = rec
    return list(by_key.values())
