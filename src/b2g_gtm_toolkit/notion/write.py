from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional, Protocol

from b2g_gtm_toolkit.models.business import BusinessProfile, ICP
from b2g_gtm_toolkit.models.gtm import GtmOutput, TargetAccount
from b2g_gtm_toolkit.models.secop import SecopNormalizedRecord
from b2g_gtm_toolkit.notion.read import target_account_from_page
from b2g_gtm_toolkit.notion.dedupe_norm import (
    collapse_whitespace,
    entity_name_normalized,
    municipality_normalized,
    nit_digits_normalized,
)
from b2g_gtm_toolkit.utils.ids import normalize_text


class NotionWriterLike(Protocol):
    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]: ...
    def create_page(
        self,
        database_id: str,
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]: ...
    def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]: ...


@dataclass
class WriteResult:
    action: str
    page_id: Optional[str]
    properties: Dict[str, Any]


@dataclass
class WorkflowImportResult:
    business_profile: WriteResult
    icp: WriteResult
    target_accounts: List[WriteResult]
    secop_records: List[WriteResult]
    matched_secop_records: int
    augmented_target_account_nits: int


@dataclass
class SecopResearchSyncResult:
    secop_records: List[WriteResult]
    target_account_ref: Optional[str]
    target_account_page_id: Optional[str]
    target_account_status: str


_NOTION_PAGE_ID_RE = re.compile(
    r"^(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"
)
_GENERIC_ENTITY_WORDS = {
    "alcaldia",
    "alcaldía",
    "municipal",
    "municipio",
    "distrito",
    "gobernacion",
    "gobernación",
    "departamento",
    "de",
    "del",
    "la",
    "el",
}


def _title(value: Optional[str]) -> Dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": value or ""}}]}


def _rich_text(value: Optional[str]) -> Dict[str, Any]:
    return {"rich_text": [{"type": "text", "text": {"content": value or ""}}]}


def _select(value: Optional[str]) -> Dict[str, Any]:
    if not value:
        return {"select": None}
    return {"select": {"name": value}}


def _multi_select(values: Optional[List[str]]) -> Dict[str, Any]:
    seen: set[str] = set()
    options = []
    for value in values or []:
        name = _notion_option_name(value)
        if name and name not in seen:
            options.append({"name": name})
            seen.add(name)
    return {"multi_select": options}


def _notion_option_name(value: Optional[str]) -> str:
    name = (value or "").replace(",", " -").strip()
    # Notion select option names have a short length limit; keep long narrative
    # fields deterministic while avoiding API rejection.
    return name[:100]


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


def _joined_text(values: Optional[List[str]]) -> str:
    return "\n".join(v for v in (values or []) if v)


def _looks_like_notion_page_id(value: Optional[str]) -> bool:
    return bool(value and _NOTION_PAGE_ID_RE.match(value.strip()))


def _nit_key(value: Optional[str]) -> str:
    return nit_digits_normalized(value)


def _significant_tokens(value: Optional[str]) -> set[str]:
    normalized = normalize_text(value or "")
    tokens = re.findall(r"[a-z0-9]+", normalized)
    return {token for token in tokens if token not in _GENERIC_ENTITY_WORDS}


def _entity_name_matches(record: SecopNormalizedRecord, account: TargetAccount) -> bool:
    buyer_tokens = _significant_tokens(record.buyer_name)
    account_tokens = _significant_tokens(account.normalized_name or account.name)
    municipality_tokens = _significant_tokens(account.municipality)
    department_tokens = _significant_tokens(account.department)

    if not buyer_tokens or not account_tokens:
        return False
    if account_tokens and account_tokens.issubset(buyer_tokens):
        return True
    if municipality_tokens and municipality_tokens.issubset(buyer_tokens):
        return True
    if department_tokens and department_tokens.issubset(buyer_tokens) and account_tokens & buyer_tokens:
        return True
    return False


def _augment_target_account_nits(
    accounts: List[TargetAccount],
    records: List[SecopNormalizedRecord],
) -> tuple[List[TargetAccount], int]:
    augmented: List[TargetAccount] = []
    count = 0
    for account in accounts:
        if account.nit:
            augmented.append(account)
            continue
        candidates: Dict[str, str] = {}
        for record in records:
            key = _nit_key(record.buyer_nit)
            if key and _entity_name_matches(record, account):
                candidates[key] = record.buyer_nit or key
        if len(candidates) == 1:
            augmented.append(account.model_copy(update={"nit": next(iter(candidates.values()))}))
            count += 1
        else:
            augmented.append(account)
    return augmented, count


def _matched_target_index(
    record: SecopNormalizedRecord,
    accounts: List[TargetAccount],
) -> Optional[int]:
    buyer_nit_key = _nit_key(record.buyer_nit)
    if buyer_nit_key:
        for idx, account in enumerate(accounts):
            if _nit_key(account.nit) == buyer_nit_key:
                return idx

    for idx, account in enumerate(accounts):
        if _entity_name_matches(record, account):
            return idx
    return None


def business_profile_properties(profile: BusinessProfile) -> Dict[str, Any]:
    return {
        "Name": _title(profile.name),
        "Offer Summary": _rich_text(profile.offer_summary),
        "Products Services": _multi_select(profile.products_services),
        "Current Customers": _multi_select(profile.current_customers),
        "Best Customers": _multi_select(profile.best_customers),
        "Poor Fit Customers": _multi_select(profile.poor_fit_customers),
        "Competitors": _multi_select(profile.competitors),
        "Company Stage": _select(profile.company_stage.value),
        "Regions Served": _multi_select(profile.regions_served),
        "Constraints": _rich_text(_joined_text(profile.constraints)),
    }


def icp_properties(icp: ICP) -> Dict[str, Any]:
    props: Dict[str, Any] = {
        "Name": _title(icp.name),
        "Target Entity Types": _multi_select(icp.target_entity_types),
        "Target Categories": _multi_select(icp.target_categories),
        "Target Regions": _multi_select(icp.target_regions),
        "Fit Criteria": _rich_text(_joined_text(icp.fit_criteria)),
        "Disqualifiers": _rich_text(_joined_text(icp.disqualifiers)),
        "Buying Triggers": _rich_text(_joined_text(icp.buying_triggers)),
        "Observable Signals": _rich_text(_joined_text(icp.observable_signals)),
        "Confidence Level": _select(icp.confidence_level.value),
        "Evidence Summary": _rich_text(icp.evidence_summary),
        "Approval Status": _select(icp.approval_status.value),
    }
    if icp.business_profile_ref:
        props["Business Profile"] = _relation([icp.business_profile_ref])
    return props


def target_account_properties(account: TargetAccount) -> Dict[str, Any]:
    display_name = collapse_whitespace(account.name) or account.name
    nit_store = nit_digits_normalized(account.nit) if account.nit else None
    norm_name_store = entity_name_normalized(
        normalized_name=account.normalized_name,
        display_name=account.name,
    )
    mun_store = municipality_normalized(account.municipality) if account.municipality else ""
    props: Dict[str, Any] = {
        "Name": _title(display_name),
        "Normalized Name": _rich_text(norm_name_store or None),
        "Entity Type": _select(account.entity_type),
        "NIT": _rich_text(nit_store if nit_store else (account.nit.strip() if account.nit else None)),
        "Department": _select(account.department),
        "Municipality": _rich_text(mun_store or None),
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
    children: Optional[List[Dict[str, Any]]] = None,
) -> WriteResult:
    if client is None:
        return WriteResult(action="dry_run_create", page_id=None, properties=properties)
    existing = client.query_database(database_id, dedupe_key) or []
    if existing:
        page_id = existing[0].get("id")
        client.update_page(page_id, properties)
        if children and hasattr(client, "append_page_children"):
            client.append_page_children(page_id, children)  # type: ignore[attr-defined]
        return WriteResult(action="update", page_id=page_id, properties=properties)
    if children:
        created = client.create_page(database_id, properties, children)
    else:
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


def lookup_filter_for_target_account_ref(target_account_ref: str) -> Dict[str, Any]:
    ref = (target_account_ref or "").strip()
    clauses: List[Dict[str, Any]] = [
        {"property": "Name", "title": {"equals": ref}},
        {
            "property": "Normalized Name",
            "rich_text": {"equals": entity_name_normalized(normalized_name=None, display_name=ref)},
        },
    ]
    nk = nit_digits_normalized(ref)
    if nk:
        clauses.append({"property": "NIT", "rich_text": {"equals": nk}})
    collapsed = collapse_whitespace(ref)
    if collapsed and collapsed != ref:
        clauses.append({"property": "Name", "title": {"equals": collapsed}})
    return clauses[0] if len(clauses) == 1 else {"or": clauses}


def _resolve_target_account_ref(
    *,
    target_account_ref: Optional[str],
    target_accounts_database_id: Optional[str],
    client: Optional[NotionWriterLike],
) -> tuple[Optional[str], str]:
    if not target_account_ref:
        return None, "not_provided"
    if _looks_like_notion_page_id(target_account_ref):
        return target_account_ref, "direct_page_id"
    if not client or not target_accounts_database_id:
        return None, "not_resolved"

    matches = client.query_database(
        target_accounts_database_id,
        lookup_filter_for_target_account_ref(target_account_ref),
    )
    if len(matches) == 1 and matches[0].get("id"):
        return matches[0]["id"], "resolved"
    if len(matches) > 1:
        return None, "ambiguous"
    return None, "not_resolved"


def _secop_record_for_write(
    record: SecopNormalizedRecord,
    target_account_page_id: Optional[str],
) -> SecopNormalizedRecord:
    if target_account_page_id:
        return record.model_copy(update={"matched_account_id": target_account_page_id})
    if record.matched_account_id and not _looks_like_notion_page_id(record.matched_account_id):
        return record.model_copy(update={"matched_account_id": None})
    return record


def sync_secop_research_to_notion(
    *,
    records: List[SecopNormalizedRecord],
    database_ids: Dict[str, str],
    client: Optional[NotionWriterLike] = None,
    target_account_ref: Optional[str] = None,
) -> SecopResearchSyncResult:
    target_account_page_id, target_account_status = _resolve_target_account_ref(
        target_account_ref=target_account_ref,
        target_accounts_database_id=database_ids.get("B2G Target Accounts"),
        client=client,
    )
    results: List[WriteResult] = []
    for record in records:
        record_for_write = _secop_record_for_write(record, target_account_page_id)
        results.append(
            upsert_page(
                database_ids["B2G SECOP Research"],
                secop_record_properties(record_for_write),
                dedupe_filter_for_secop(record),
                client,
            )
        )
    return SecopResearchSyncResult(
        secop_records=results,
        target_account_ref=target_account_ref,
        target_account_page_id=target_account_page_id,
        target_account_status=target_account_status,
    )


def upsert_gtm_output(
    database_id: str,
    output: GtmOutput,
    client: Optional[NotionWriterLike] = None,
) -> WriteResult:
    from b2g_gtm_toolkit.notion.output_mapper import (
        dedupe_filter_for_gtm_output,
        gtm_output_body_children,
        gtm_output_properties,
    )

    return upsert_page(
        database_id,
        gtm_output_properties(output),
        dedupe_filter_for_gtm_output(output),
        client,
        children=gtm_output_body_children(output),
    )


def dedupe_filter_for_business_profile(profile: BusinessProfile) -> Dict[str, Any]:
    return {"property": "Name", "title": {"equals": profile.name}}


def dedupe_filter_for_icp(icp: ICP) -> Dict[str, Any]:
    return {"property": "Name", "title": {"equals": icp.name}}


def _unique_filter_arms(arms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for arm in arms:
        key = str(arm)
        if key not in seen:
            seen.add(key)
            out.append(arm)
    return out


def target_account_match_filter(account: TargetAccount) -> Dict[str, Any]:
    """OR across NIT, normalized name(+muni), and legacy title/muni variants (dedupe-safe)."""
    arms: List[Dict[str, Any]] = []
    nit = nit_digits_normalized(account.nit)
    name_key = entity_name_normalized(
        normalized_name=account.normalized_name,
        display_name=account.name,
    )
    mun_key = municipality_normalized(account.municipality) if account.municipality else ""
    title_plain = collapse_whitespace(account.name) or account.name
    raw_muni = collapse_whitespace(account.municipality or "")

    if nit:
        arms.append({"property": "NIT", "rich_text": {"equals": nit}})
    if name_key and mun_key:
        arms.append(
            {
                "and": [
                    {"property": "Normalized Name", "rich_text": {"equals": name_key}},
                    {"property": "Municipality", "rich_text": {"equals": mun_key}},
                ]
            }
        )
    elif name_key:
        arms.append({"property": "Normalized Name", "rich_text": {"equals": name_key}})
    if title_plain and mun_key:
        arms.append(
            {
                "and": [
                    {"property": "Name", "title": {"equals": title_plain}},
                    {"property": "Municipality", "rich_text": {"equals": mun_key}},
                ]
            }
        )
    elif title_plain and not mun_key:
        arms.append({"property": "Name", "title": {"equals": title_plain}})
    if title_plain and raw_muni and raw_muni != mun_key:
        arms.append(
            {
                "and": [
                    {"property": "Name", "title": {"equals": title_plain}},
                    {"property": "Municipality", "rich_text": {"equals": raw_muni}},
                ]
            }
        )
    arms = _unique_filter_arms(arms)
    if not arms:
        arms = [{"property": "Name", "title": {"equals": title_plain}}]
    return arms[0] if len(arms) == 1 else {"or": arms}


def dedupe_filter_for_target_account(account: TargetAccount) -> Dict[str, Any]:
    return target_account_match_filter(account)


def pick_canonical_target_account_page(existing: List[Dict[str, Any]], account: TargetAccount) -> str:
    nit = nit_digits_normalized(account.nit)
    pool = existing
    if nit:
        matched = [
            page
            for page in existing
            if nit_digits_normalized(target_account_from_page(page).get("nit")) == nit
        ]
        if matched:
            pool = matched
    ordered = sorted(pool, key=lambda page: page.get("created_time") or "")
    return ordered[0]["id"]


def upsert_target_account(
    *,
    database_id: str,
    account: TargetAccount,
    client: Optional[NotionWriterLike] = None,
) -> WriteResult:
    props = target_account_properties(account)
    if client is None:
        return WriteResult(action="dry_run_create", page_id=None, properties=props)
    existing = client.query_database(database_id, target_account_match_filter(account)) or []
    if existing:
        page_id = pick_canonical_target_account_page(existing, account)
        client.update_page(page_id, props)
        return WriteResult(action="update", page_id=page_id, properties=props)
    created = client.create_page(database_id, props)
    return WriteResult(action="create", page_id=created.get("id"), properties=props)


def import_workflow_to_notion(
    *,
    business_profile: BusinessProfile,
    icp: ICP,
    target_accounts: List[TargetAccount],
    secop_records: List[SecopNormalizedRecord],
    database_ids: Dict[str, str],
    client: Optional[NotionWriterLike] = None,
) -> WorkflowImportResult:
    business_result = upsert_page(
        database_ids["B2G Business Profiles"],
        business_profile_properties(business_profile),
        dedupe_filter_for_business_profile(business_profile),
        client,
    )

    icp_for_write = icp
    if business_result.page_id:
        icp_for_write = icp.model_copy(update={"business_profile_ref": business_result.page_id})
    icp_result = upsert_page(
        database_ids["B2G ICPs"],
        icp_properties(icp_for_write),
        dedupe_filter_for_icp(icp),
        client,
    )

    accounts_for_write, augmented_nits = _augment_target_account_nits(target_accounts, secop_records)
    account_results: List[WriteResult] = []
    for account in accounts_for_write:
        account_for_write = account
        if icp_result.page_id:
            account_for_write = account.model_copy(update={"icp_ref": icp_result.page_id})
        account_results.append(
            upsert_target_account(
                database_id=database_ids["B2G Target Accounts"],
                account=account_for_write,
                client=client,
            )
        )

    account_page_ids = [result.page_id for result in account_results]
    matched_secop = 0
    secop_results: List[WriteResult] = []
    for record in secop_records:
        matched_page_id = record.matched_account_id if _looks_like_notion_page_id(record.matched_account_id) else None
        matched_index = None if matched_page_id else _matched_target_index(record, accounts_for_write)
        if matched_index is not None:
            matched_page_id = account_page_ids[matched_index]
        record_for_write = record
        if matched_page_id or matched_index is not None:
            matched_secop += 1
        if matched_page_id:
            record_for_write = record.model_copy(update={"matched_account_id": matched_page_id})
        secop_results.append(
            upsert_page(
                database_ids["B2G SECOP Research"],
                secop_record_properties(record_for_write),
                dedupe_filter_for_secop(record),
                client,
            )
        )

    return WorkflowImportResult(
        business_profile=business_result,
        icp=icp_result,
        target_accounts=account_results,
        secop_records=secop_results,
        matched_secop_records=matched_secop,
        augmented_target_account_nits=augmented_nits,
    )
