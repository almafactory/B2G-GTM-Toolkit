from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple


class NotionReaderLike(Protocol):
    def retrieve_page(self, page_id: str) -> Dict[str, Any]: ...
    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]: ...


@dataclass
class NotionBuilderInput:
    opportunity: Dict[str, Any]
    account: Dict[str, Any]
    research: List[Dict[str, Any]]
    prior_outputs: List[Dict[str, Any]] = field(default_factory=list)

    def builder_args(self) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        return self.opportunity, self.account, self.research


def _props(page: Dict[str, Any]) -> Dict[str, Any]:
    return page.get("properties") or {}


def _plain_text(items: List[Dict[str, Any]]) -> Optional[str]:
    text = "".join(item.get("plain_text") or item.get("text", {}).get("content") or "" for item in items)
    return text or None


def _title(properties: Dict[str, Any], name: str) -> Optional[str]:
    value = properties.get(name) or {}
    return _plain_text(value.get("title") or [])


def _rich_text(properties: Dict[str, Any], name: str) -> Optional[str]:
    value = properties.get(name) or {}
    return _plain_text(value.get("rich_text") or [])


def _select(properties: Dict[str, Any], name: str) -> Optional[str]:
    selected = (properties.get(name) or {}).get("select")
    return selected.get("name") if selected else None


def _multi_select(properties: Dict[str, Any], name: str) -> List[str]:
    return [item.get("name") for item in (properties.get(name) or {}).get("multi_select", []) if item.get("name")]


def _number(properties: Dict[str, Any], name: str) -> Optional[float]:
    value = (properties.get(name) or {}).get("number")
    return value if value is not None else None


def _url(properties: Dict[str, Any], name: str) -> Optional[str]:
    return (properties.get(name) or {}).get("url")


def _date(properties: Dict[str, Any], name: str) -> Optional[str]:
    value = (properties.get(name) or {}).get("date")
    if not value:
        return None
    return value.get("start")


def _relation_ids(properties: Dict[str, Any], name: str) -> List[str]:
    return [item.get("id") for item in (properties.get(name) or {}).get("relation", []) if item.get("id")]


def _location(municipality: Optional[str], department: Optional[str]) -> Optional[str]:
    parts = [part for part in [municipality, department] if part]
    return ", ".join(parts) if parts else None


def opportunity_from_page(page: Dict[str, Any]) -> Dict[str, Any]:
    properties = _props(page)
    return {
        "id": page.get("id"),
        "title": _title(properties, "Title") or _title(properties, "Name"),
        "summary": _rich_text(properties, "Summary"),
        "status": _select(properties, "Status"),
        "source_platform": _select(properties, "Source Platform"),
        "source_url": _url(properties, "Source URL"),
        "estimated_value": _number(properties, "Estimated Value"),
        "deadline": _date(properties, "Deadline"),
        "modality": _select(properties, "Modality"),
        "requirements_summary": _rich_text(properties, "Requirements Summary"),
        "fit_score": _number(properties, "Fit Score"),
        "fit_rationale": _rich_text(properties, "Fit Rationale"),
        "pursuit_recommendation": _rich_text(properties, "Pursuit Recommendation"),
        "next_action": _rich_text(properties, "Next Action"),
        "approval_status": _select(properties, "Approval Status"),
        "target_account_ref": (_relation_ids(properties, "Target Account") or [None])[0],
        "research_record_refs": _relation_ids(properties, "Research Records"),
    }


def target_account_from_page(page: Dict[str, Any]) -> Dict[str, Any]:
    properties = _props(page)
    municipality = _rich_text(properties, "Municipality")
    department = _select(properties, "Department")
    return {
        "id": page.get("id"),
        "name": _title(properties, "Name"),
        "normalized_name": _rich_text(properties, "Normalized Name"),
        "entity_type": _select(properties, "Entity Type"),
        "nit": _rich_text(properties, "NIT"),
        "department": department,
        "municipality": municipality,
        "location": _location(municipality, department),
        "category": _select(properties, "Category"),
        "fit_score": _number(properties, "Fit Score"),
        "fit_rationale": _rich_text(properties, "Fit Rationale"),
        "research_status": _select(properties, "Research Status"),
        "last_researched_at": _date(properties, "Last Researched At"),
    }


def secop_research_from_page(page: Dict[str, Any]) -> Dict[str, Any]:
    properties = _props(page)
    return {
        "id": page.get("id"),
        "object": _title(properties, "Object"),
        "source_platform": _select(properties, "Source Platform"),
        "source_dataset": _rich_text(properties, "Source Dataset"),
        "source_record_id": _rich_text(properties, "Source Record ID"),
        "source_url": _url(properties, "Source URL"),
        "process_id": _rich_text(properties, "Process ID"),
        "contract_id": _rich_text(properties, "Contract ID"),
        "buyer_name": _rich_text(properties, "Buyer Name"),
        "buyer_nit": _rich_text(properties, "Buyer NIT"),
        "supplier_name": _rich_text(properties, "Supplier Name"),
        "supplier_nit": _rich_text(properties, "Supplier NIT"),
        "modality": _select(properties, "Modality"),
        "status": _select(properties, "Status"),
        "contract_value": _number(properties, "Contract Value"),
        "currency": _select(properties, "Currency"),
        "publication_date": _date(properties, "Publication Date"),
        "award_date": _date(properties, "Award Date"),
        "deadline": _date(properties, "Deadline"),
        "unspsc_codes": _multi_select(properties, "UNSPSC Codes"),
        "target_account_ref": (_relation_ids(properties, "Target Account") or [None])[0],
        "run_id": _rich_text(properties, "Run ID"),
    }


def gtm_output_from_page(page: Dict[str, Any]) -> Dict[str, Any]:
    properties = _props(page)
    return {
        "id": page.get("id"),
        "title": _title(properties, "Title") or _title(properties, "Name"),
        "type": _select(properties, "Type"),
        "content": _rich_text(properties, "Content"),
        "source_summary": _rich_text(properties, "Source Summary"),
        "approval_status": _select(properties, "Approval Status"),
        "target_account_ref": (_relation_ids(properties, "Target Account") or [None])[0],
        "opportunity_ref": (_relation_ids(properties, "Opportunity") or [None])[0],
        "research_record_refs": _relation_ids(properties, "Research Records"),
    }


def resolve_opportunity_input(
    *,
    opportunity_page_id: str,
    database_ids: Dict[str, str],
    client: NotionReaderLike,
) -> NotionBuilderInput:
    opportunity_page = client.retrieve_page(opportunity_page_id)
    opportunity = opportunity_from_page(opportunity_page)

    account = {}
    account_page_id = opportunity.get("target_account_ref")
    if account_page_id:
        account = target_account_from_page(client.retrieve_page(account_page_id))

    research_pages = _retrieve_related_pages(client, opportunity.get("research_record_refs") or [])
    if not research_pages and account_page_id and "B2G SECOP Research" in database_ids:
        research_pages = client.query_database(
            database_ids["B2G SECOP Research"],
            relation_contains_filter("Target Account", account_page_id),
        )

    prior_outputs = []
    if "B2G GTM Outputs" in database_ids:
        prior_outputs = query_gtm_outputs(
            client=client,
            database_id=database_ids["B2G GTM Outputs"],
            opportunity_page_id=opportunity_page_id,
            target_account_page_id=account_page_id,
        )

    return NotionBuilderInput(
        opportunity=opportunity,
        account=account,
        research=[secop_research_from_page(page) for page in research_pages],
        prior_outputs=[gtm_output_from_page(page) for page in prior_outputs],
    )


def resolve_target_account_input(
    *,
    target_account_page_id: str,
    database_ids: Dict[str, str],
    client: NotionReaderLike,
) -> NotionBuilderInput:
    account = target_account_from_page(client.retrieve_page(target_account_page_id))
    research_pages = []
    if "B2G SECOP Research" in database_ids:
        research_pages = client.query_database(
            database_ids["B2G SECOP Research"],
            relation_contains_filter("Target Account", target_account_page_id),
        )

    prior_outputs = []
    if "B2G GTM Outputs" in database_ids:
        prior_outputs = query_gtm_outputs(
            client=client,
            database_id=database_ids["B2G GTM Outputs"],
            target_account_page_id=target_account_page_id,
        )

    return NotionBuilderInput(
        opportunity={"title": account.get("name")},
        account=account,
        research=[secop_research_from_page(page) for page in research_pages],
        prior_outputs=[gtm_output_from_page(page) for page in prior_outputs],
    )


def relation_contains_filter(property_name: str, page_id: str) -> Dict[str, Any]:
    return {"property": property_name, "relation": {"contains": page_id}}


def query_gtm_outputs(
    *,
    client: NotionReaderLike,
    database_id: str,
    opportunity_page_id: Optional[str] = None,
    target_account_page_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    clauses = []
    if opportunity_page_id:
        clauses.append(relation_contains_filter("Opportunity", opportunity_page_id))
    if target_account_page_id:
        clauses.append(relation_contains_filter("Target Account", target_account_page_id))
    if not clauses:
        return []
    filter_payload = clauses[0] if len(clauses) == 1 else {"or": clauses}
    return client.query_database(database_id, filter_payload)


def _retrieve_related_pages(client: NotionReaderLike, page_ids: List[str]) -> List[Dict[str, Any]]:
    return [client.retrieve_page(page_id) for page_id in page_ids]
