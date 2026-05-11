from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from b2g_gtm_toolkit.models.business import BusinessProfile, ICP
from b2g_gtm_toolkit.models.gtm import TargetAccount
from b2g_gtm_toolkit.models.secop import Provenance, SecopNormalizedRecord, SourcePlatform
from b2g_gtm_toolkit.notion.write import import_workflow_to_notion


DB_IDS = {
    "B2G Business Profiles": "db_bp",
    "B2G ICPs": "db_icp",
    "B2G Target Accounts": "db_accounts",
    "B2G SECOP Research": "db_secop",
}


class StatefulFakeNotionClient:
    def __init__(self) -> None:
        self.creates: list[dict[str, Any]] = []
        self.updates: list[dict[str, Any]] = []
        self.pages: dict[str, dict[str, Any]] = {}
        self.page_databases: dict[str, str] = {}

    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]):
        for page_id, properties in self.pages.items():
            if self.page_databases[page_id] == database_id and _matches_filter(properties, filter):
                return [{"id": page_id, "properties": properties}]
        return []

    def create_page(self, database_id: str, properties: Dict[str, Any]):
        page_id = f"page_{len(self.creates) + 1}"
        self.creates.append({"database_id": database_id, "properties": properties})
        self.pages[page_id] = properties
        self.page_databases[page_id] = database_id
        return {"id": page_id}

    def update_page(self, page_id: str, properties: Dict[str, Any]):
        self.updates.append({"page_id": page_id, "properties": properties})
        self.pages[page_id] = properties
        return {"id": page_id}


def _matches_filter(properties: Dict[str, Any], filter: Optional[Dict[str, Any]]) -> bool:
    if not filter:
        return True
    if "and" in filter:
        return all(_matches_filter(properties, clause) for clause in filter["and"])
    prop = filter["property"]
    if "title" in filter:
        return _prop_value(properties, prop, "title") == filter["title"]["equals"]
    if "rich_text" in filter:
        return _prop_value(properties, prop, "rich_text") == filter["rich_text"]["equals"]
    if "select" in filter:
        return _prop_value(properties, prop, "select") == filter["select"]["equals"]
    return False


def _prop_value(properties: Dict[str, Any], prop: str, kind: str) -> Optional[str]:
    value = properties.get(prop) or {}
    if kind == "title":
        items = value.get("title") or []
        return items[0]["text"]["content"] if items else None
    if kind == "rich_text":
        items = value.get("rich_text") or []
        return items[0]["text"]["content"] if items else None
    if kind == "select":
        selected = value.get("select")
        return selected.get("name") if selected else None
    return None


def _business_profile() -> BusinessProfile:
    return BusinessProfile(
        name="SIIF Web",
        offer_summary="ERP para entidades publicas",
        products_services=["ERP"],
        company_stage="growth",
    )


def _icp() -> ICP:
    return ICP(
        name="Alcaldias intermedias categoria 1 a 4",
        target_entity_types=["alcaldia"],
        confidence_level="high",
    )


def _target_account() -> TargetAccount:
    return TargetAccount(
        name="Alcaldia de Soledad",
        entity_type="alcaldia",
        department="Atlantico",
        municipality="Soledad",
        fit_score=88,
    )


def _secop_record() -> SecopNormalizedRecord:
    return SecopNormalizedRecord(
        source_platform=SourcePlatform.SECOP_II,
        source_dataset="secop_ii_contratos",
        source_record_id="soledad-1",
        buyer_name="MUNICIPIO DE SOLEDAD",
        buyer_nit="890106291",
        object="Servicio de software financiero",
        provenance=Provenance(
            source_dataset="secop_ii_contratos",
            retrieved_at=datetime.now(timezone.utc),
            raw_payload_hash="hash-soledad-1",
        ),
        run_id="run-soledad",
    )


def test_import_workflow_upserts_and_relates_records() -> None:
    fake = StatefulFakeNotionClient()

    result = import_workflow_to_notion(
        business_profile=_business_profile(),
        icp=_icp(),
        target_accounts=[_target_account()],
        secop_records=[_secop_record()],
        database_ids=DB_IDS,
        client=fake,
    )

    assert result.business_profile.action == "create"
    assert result.icp.action == "create"
    assert result.target_accounts[0].action == "create"
    assert result.secop_records[0].action == "create"
    assert result.augmented_target_account_nits == 1
    assert result.matched_secop_records == 1

    icp_props = fake.pages[result.icp.page_id]
    assert icp_props["Business Profile"]["relation"][0]["id"] == result.business_profile.page_id

    account_props = fake.pages[result.target_accounts[0].page_id]
    assert account_props["ICP"]["relation"][0]["id"] == result.icp.page_id
    assert account_props["NIT"]["rich_text"][0]["text"]["content"] == "890106291"

    secop_props = fake.pages[result.secop_records[0].page_id]
    assert secop_props["Target Account"]["relation"][0]["id"] == result.target_accounts[0].page_id


def test_repeated_import_updates_existing_pages() -> None:
    fake = StatefulFakeNotionClient()
    first = import_workflow_to_notion(
        business_profile=_business_profile(),
        icp=_icp(),
        target_accounts=[_target_account()],
        secop_records=[_secop_record()],
        database_ids=DB_IDS,
        client=fake,
    )

    second = import_workflow_to_notion(
        business_profile=_business_profile(),
        icp=_icp(),
        target_accounts=[_target_account()],
        secop_records=[_secop_record()],
        database_ids=DB_IDS,
        client=fake,
    )

    assert second.business_profile.action == "update"
    assert second.icp.action == "update"
    assert second.target_accounts[0].action == "update"
    assert second.secop_records[0].action == "update"
    assert second.business_profile.page_id == first.business_profile.page_id
    assert second.icp.page_id == first.icp.page_id
    assert second.target_accounts[0].page_id == first.target_accounts[0].page_id
    assert second.secop_records[0].page_id == first.secop_records[0].page_id
    assert len(fake.creates) == 4
    assert len(fake.updates) == 4
    assert len(fake.pages) == 4


def test_multi_select_values_are_safe_for_notion() -> None:
    fake = StatefulFakeNotionClient()
    profile = _business_profile().model_copy(
        update={
            "best_customers": [
                "Alcaldias categoria 1 a 4, especialmente Costa Caribe, con presupuesto suficiente"
            ]
        }
    )

    result = import_workflow_to_notion(
        business_profile=profile,
        icp=_icp(),
        target_accounts=[_target_account()],
        secop_records=[_secop_record()],
        database_ids=DB_IDS,
        client=fake,
    )

    profile_props = fake.pages[result.business_profile.page_id]
    option_name = profile_props["Best Customers"]["multi_select"][0]["name"]
    assert "," not in option_name
    assert len(option_name) <= 100
