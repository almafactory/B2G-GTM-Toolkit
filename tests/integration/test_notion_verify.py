from __future__ import annotations

from typing import Any, Dict, List, Optional

from b2g_gtm_toolkit.cli import _apply_database_setup
from b2g_gtm_toolkit.notion.schema import DEFAULT_MANIFEST
from b2g_gtm_toolkit.notion.verify import plan_setup, verify_workspace


def _build_db_payload(
    spec,
    *,
    relation_target_key: str = "database_id",
    omit_properties: Optional[set[str]] = None,
) -> Dict[str, Any]:
    omit = omit_properties or set()
    properties: Dict[str, Any] = {}
    for prop in spec.properties:
        if prop.name in omit:
            continue
        block: Dict[str, Any] = {"type": prop.type.value, prop.type.value: {}}
        if prop.type.value == "relation":
            block["relation"] = {relation_target_key: "fake-id-" + (prop.relation_database or "")}
        properties[prop.name] = block
    return {
        "id": "db-" + spec.name.replace(" ", "-").lower(),
        "title": [{"plain_text": spec.name}],
        "properties": properties,
    }


class FakeNotionClient:
    def __init__(self, databases: List[Dict[str, Any]]):
        self._by_id = {db["id"]: db for db in databases}
        self._by_title: Dict[str, Dict[str, Any]] = {}
        self.search_queries: List[str] = []
        for db in databases:
            title = db.get("title")
            if isinstance(title, list) and title:
                self._by_title[title[0].get("plain_text", "")] = db

    def search_databases(self, query: str):
        self.search_queries.append(query)
        match = self._by_title.get(query)
        return [match] if match else []

    def retrieve_database(self, database_id: str) -> Optional[Dict[str, Any]]:
        return self._by_id.get(database_id)

    def query_database(self, database_id, filter):
        return []

    def create_page(self, database_id, properties):
        return {"id": "new-page"}

    def update_page(self, page_id, properties):
        return {"id": page_id}


class FakeSetupClient:
    def __init__(self):
        self.updated_databases: List[tuple[str, Dict[str, Any]]] = []

    def create_database(self, parent_page_id: str, title: str, properties):
        raise AssertionError("test fixture should not create databases")

    def update_database(self, database_id: str, properties):
        self.updated_databases.append((database_id, properties))
        return {"id": database_id, "properties": properties}


def test_verify_all_present():
    databases = [_build_db_payload(spec) for spec in DEFAULT_MANIFEST.databases]
    client = FakeNotionClient(databases)
    report = verify_workspace(DEFAULT_MANIFEST, client)
    assert report.ok is True
    assert all(db.found for db in report.databases)
    plan = plan_setup(DEFAULT_MANIFEST, report)
    assert plan.creates == []
    assert plan.updates == []
    assert len(plan.noops) == len(DEFAULT_MANIFEST.databases)


def test_verify_uses_known_ids_without_search_fallback():
    databases = [_build_db_payload(spec) for spec in DEFAULT_MANIFEST.databases]
    client = FakeNotionClient(databases)
    known_ids = {
        spec.name: "db-" + spec.name.replace(" ", "-").lower()
        for spec in DEFAULT_MANIFEST.databases
    }

    report = verify_workspace(
        DEFAULT_MANIFEST,
        client,
        known_ids,
        allow_search_fallback=False,
    )

    assert report.ok is True
    assert client.search_queries == []


def test_verify_one_database_missing():
    payloads = [
        _build_db_payload(spec)
        for spec in DEFAULT_MANIFEST.databases
        if spec.name != "B2G Signals"
    ]
    client = FakeNotionClient(payloads)
    report = verify_workspace(DEFAULT_MANIFEST, client)
    assert report.ok is False
    missing = [db for db in report.databases if not db.found]
    assert len(missing) == 1
    assert missing[0].name == "B2G Signals"
    plan = plan_setup(DEFAULT_MANIFEST, report)
    assert any(a.database == "B2G Signals" for a in plan.creates)
    assert len(plan.creates) == 1


def test_verify_property_type_mismatch():
    spec = next(db for db in DEFAULT_MANIFEST.databases if db.name == "B2G Target Accounts")
    payload = _build_db_payload(spec)
    payload["properties"]["Fit Score"] = {"type": "rich_text", "rich_text": {}}
    other = [
        _build_db_payload(s) for s in DEFAULT_MANIFEST.databases if s.name != spec.name
    ]
    client = FakeNotionClient(other + [payload])
    report = verify_workspace(DEFAULT_MANIFEST, client)
    assert report.ok is False
    target = next(db for db in report.databases if db.name == "B2G Target Accounts")
    assert target.found
    assert any(p.property == "Fit Score" for p in target.mistyped_properties)
    plan = plan_setup(DEFAULT_MANIFEST, report)
    assert any(
        a.database == "B2G Target Accounts" and "Fit Score" in a.detail
        for a in plan.updates
    )


def test_verify_relation_target_accepts_data_source_id():
    databases = [
        _build_db_payload(spec, relation_target_key="data_source_id")
        for spec in DEFAULT_MANIFEST.databases
    ]
    client = FakeNotionClient(databases)

    report = verify_workspace(DEFAULT_MANIFEST, client)

    assert report.ok is True
    assert all(not db.missing_relations for db in report.databases)


def test_apply_setup_maps_missing_relations_to_data_source_ids():
    target_accounts = next(db for db in DEFAULT_MANIFEST.databases if db.name == "B2G Target Accounts")
    payloads = []
    for spec in DEFAULT_MANIFEST.databases:
        missing = {"Owner", "ICP"} if spec.name == target_accounts.name else set()
        payloads.append(_build_db_payload(spec, omit_properties=missing))
    report = verify_workspace(DEFAULT_MANIFEST, FakeNotionClient(payloads))
    client = FakeSetupClient()

    database_ids = _apply_database_setup(DEFAULT_MANIFEST, report, client, "parent-page")

    assert database_ids["B2G Owners"] == "db-b2g-owners"
    assert database_ids["B2G ICPs"] == "db-b2g-icps"
    assert client.updated_databases == [
        (
            "db-b2g-target-accounts",
            {
                "Owner": {
                    "relation": {
                        "data_source_id": "db-b2g-owners",
                        "type": "single_property",
                        "single_property": {},
                    }
                },
                "ICP": {
                    "relation": {
                        "data_source_id": "db-b2g-icps",
                        "type": "single_property",
                        "single_property": {},
                    }
                },
            },
        )
    ]
