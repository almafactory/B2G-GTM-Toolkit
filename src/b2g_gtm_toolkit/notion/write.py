from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from b2g_gtm_toolkit.models.gtm import TargetAccount
from b2g_gtm_toolkit.models.secop import SecopNormalizedRecord


class NotionWriterLike(Protocol):
    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]: ...
    def create_page(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]: ...
    def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]: ...


@dataclass
class WriteResult:
    action: str
    page_id: Optional[str]
    properties: Dict[str, Any]


def _title(value: Optional[str]) -> Dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": value or ""}}]}


def _rich_text(value: Optional[str]) -> Dict[str, Any]:
    return {"rich_text": [{"type": "text", "text": {"content": value or ""}}]}


def _select(value: Optional[str]) -> Dict[str, Any]:
    if not value:
        return {"select": None}
    return {"select": {"name": value}}


def _multi_select(values: Optional[List[str]]) -> Dict[str, Any]:
    return {"multi_select": [{"name": v} for v in (values or [])]}


def _number(value: Optional[float]) -> Dict[str, Any]:
    return {"number": value}


def _url(value: Optional[str]) -> Dict[str, Any]:
    return {"url": value or None}


def _date(value: Any) -> Dict[str, Any]:
    if value is None:
        return {"date": None}
    if hasattr(value, "isoformat"):
        return {"date": {"start": value.isoformat()}}
    return {"date": {"start": str(value)}}


def _relation(ids: Optional[List[str]]) -> Dict[str, Any]:
    return {"relation": [{"id": i} for i in (ids or []) if i]}


def target_account_properties(account: TargetAccount) -> Dict[str, Any]:
    props: Dict[str, Any] = {
        "Name": _title(account.name),
        "Normalized Name": _rich_text(account.normalized_name),
        "Entity Type": _select(account.entity_type),
        "NIT": _rich_text(account.nit),
        "Department": _select(account.department),
        "Municipality": _rich_text(account.municipality),
        "Category": _select(account.category),
        "Fit Score": _number(account.fit_score),
        "Fit Rationale": _rich_text(account.fit_rationale),
        "Research Status": _select(account.research_status.value if account.research_status else None),
        "Last Researched At": _date(account.last_researched_at),
    }
    if account.owner_ref:
        props["Owner"] = _relation([account.owner_ref])
    if account.icp_ref:
        props["ICP"] = _relation([account.icp_ref])
    return props


def secop_record_properties(record: SecopNormalizedRecord) -> Dict[str, Any]:
    props: Dict[str, Any] = {
        "Object": _title(record.object),
        "Source Platform": _select(record.source_platform.value),
        "Source Dataset": _rich_text(record.source_dataset),
        "Source Record ID": _rich_text(record.source_record_id),
        "Source URL": _url(record.source_url),
        "Process ID": _rich_text(record.process_id),
        "Contract ID": _rich_text(record.contract_id),
        "Buyer Name": _rich_text(record.buyer_name),
        "Buyer NIT": _rich_text(record.buyer_nit),
        "Supplier Name": _rich_text(record.supplier_name),
        "Supplier NIT": _rich_text(record.supplier_nit),
        "Modality": _select(record.modality),
        "Status": _select(record.status),
        "Contract Value": _number(record.contract_value),
        "Currency": _select(record.currency),
        "Publication Date": _date(record.publication_date),
        "Award Date": _date(record.award_date),
        "Deadline": _date(record.deadline),
        "UNSPSC Codes": _multi_select(record.unspsc_codes),
        "Run ID": _rich_text(record.run_id),
        "Raw Payload Hash": _rich_text(record.provenance.raw_payload_hash),
    }
    if record.matched_account_id:
        props["Target Account"] = _relation([record.matched_account_id])
    return props


def upsert_page(
    database_id: str,
    properties: Dict[str, Any],
    dedupe_key: Dict[str, Any],
    client: Optional[NotionWriterLike] = None,
) -> WriteResult:
    if client is None:
        return WriteResult(action="dry_run_create", page_id=None, properties=properties)
    existing = client.query_database(database_id, dedupe_key) or []
    if existing:
        page_id = existing[0].get("id")
        client.update_page(page_id, properties)
        return WriteResult(action="update", page_id=page_id, properties=properties)
    created = client.create_page(database_id, properties)
    return WriteResult(action="create", page_id=created.get("id"), properties=properties)


def update_page(
    page_id: str,
    properties: Dict[str, Any],
    client: Optional[NotionWriterLike] = None,
) -> WriteResult:
    if client is None:
        return WriteResult(action="dry_run_update", page_id=page_id, properties=properties)
    client.update_page(page_id, properties)
    return WriteResult(action="update", page_id=page_id, properties=properties)


def dedupe_filter_for_secop(record: SecopNormalizedRecord) -> Dict[str, Any]:
    return {
        "and": [
            {"property": "Source Platform", "select": {"equals": record.source_platform.value}},
            {"property": "Source Record ID", "rich_text": {"equals": record.source_record_id}},
        ]
    }
