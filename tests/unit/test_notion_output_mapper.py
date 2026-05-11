from __future__ import annotations

from typing import Any, Dict, Optional

from b2g_gtm_toolkit.models.gtm import GtmOutput, GtmOutputType
from b2g_gtm_toolkit.notion.output_mapper import (
    composite_output_storage_key,
    dedupe_filter_for_gtm_output,
    gtm_output_body_children,
    gtm_output_properties,
    legacy_output_key_for_gtm,
)
from b2g_gtm_toolkit.notion.write import upsert_gtm_output


class StatefulFakeOutputClient:
    def __init__(self) -> None:
        self.creates: list[dict[str, Any]] = []
        self.updates: list[dict[str, Any]] = []
        self.appended_children: list[dict[str, Any]] = []
        self.pages: dict[str, dict[str, Any]] = {}
        self.page_databases: dict[str, str] = {}
        self.children: dict[str, list[dict[str, Any]]] = {}

    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]):
        hits = []
        for page_id, properties in self.pages.items():
            if self.page_databases[page_id] == database_id and _matches_filter(properties, filter):
                hits.append({"id": page_id, "properties": properties})
        return hits

    def create_page(self, database_id: str, properties: Dict[str, Any], children=None):
        page_id = f"output_{len(self.creates) + 1}"
        self.creates.append({"database_id": database_id, "properties": properties, "children": children or []})
        self.pages[page_id] = properties
        self.page_databases[page_id] = database_id
        self.children[page_id] = children or []
        return {"id": page_id}

    def update_page(self, page_id: str, properties: Dict[str, Any]):
        self.updates.append({"page_id": page_id, "properties": properties})
        self.pages[page_id] = properties
        return {"id": page_id}

    def append_page_children(self, page_id: str, children):
        self.appended_children.append({"page_id": page_id, "children": children})
        self.children.setdefault(page_id, []).extend(children)
        return {"id": page_id}


def _matches_filter(properties: Dict[str, Any], filter: Optional[Dict[str, Any]]) -> bool:
    if not filter:
        return True
    if "and" in filter:
        return all(_matches_filter(properties, clause) for clause in filter["and"])
    if "or" in filter:
        return any(_matches_filter(properties, clause) for clause in filter["or"])
    prop = filter["property"]
    if "rich_text" in filter:
        return _rich_text_value(properties, prop) == filter["rich_text"]["equals"]
    return False


def _rich_text_value(properties: Dict[str, Any], prop: str) -> Optional[str]:
    items = (properties.get(prop) or {}).get("rich_text") or []
    return items[0]["text"]["content"] if items else None


def _output(content: str = "# Outreach\n\n- Evidencia SECOP\nMensaje completo") -> GtmOutput:
    return GtmOutput(
        type=GtmOutputType.outreach,
        title="outreach: Modernizacion ERP",
        content=content,
        source_summary="1 registro SECOP usado",
        source_evidence_hash="hash-evidence-1",
        target_account_ref="account-1",
        opportunity_ref="opportunity-1",
        research_record_refs=["research-1"],
    )


def test_gtm_output_maps_properties_and_dedupe_key() -> None:
    output = _output()

    props = gtm_output_properties(output)
    dedupe = dedupe_filter_for_gtm_output(output)

    assert props["Title"]["title"][0]["text"]["content"] == "outreach: Modernizacion ERP"
    assert props["Type"]["select"]["name"] == "outreach"
    assert props["Channel"]["select"]["name"] == "email"
    assert props["Approval Status"]["select"]["name"] == "draft"
    assert props["Target Account"]["relation"][0]["id"] == "account-1"
    assert props["Opportunity"]["relation"][0]["id"] == "opportunity-1"
    assert props["Research Records"]["relation"][0]["id"] == "research-1"
    composite = composite_output_storage_key(output)
    legacy = legacy_output_key_for_gtm(output)
    assert props["Output Key"]["rich_text"][0]["text"]["content"] == composite
    assert props["Source Evidence Hash"]["rich_text"][0]["text"]["content"] == "hash-evidence-1"
    assert dedupe == {
        "or": [
            {"property": "Output Key", "rich_text": {"equals": composite}},
            {"property": "Output Key", "rich_text": {"equals": legacy}},
        ],
    }



def test_gtm_output_explicit_output_key_matches_single_equals_dedupe() -> None:
    output = _output().model_copy(update={"output_key": "custom-key-fixed"})
    props = gtm_output_properties(output)
    dedupe = dedupe_filter_for_gtm_output(output)
    assert props["Output Key"]["rich_text"][0]["text"]["content"] == "custom-key-fixed"
    assert dedupe == {"property": "Output Key", "rich_text": {"equals": "custom-key-fixed"}}




def test_upsert_matches_legacy_output_key_stored_without_composite_prefix() -> None:
    fake = StatefulFakeOutputClient()
    legacy = "|".join(
        [
            GtmOutputType.outreach.value,
            "opportunity-1",
            "account-1",
            "hash-evidence-1",
        ]
    )
    seeded_id = "seed_legacy"
    fake.pages[seeded_id] = {
        "Output Key": {"rich_text": [{"type": "text", "text": {"content": legacy}}]},
    }
    fake.page_databases[seeded_id] = "db_outputs"
    outcome = upsert_gtm_output("db_outputs", _output(), fake)
    assert outcome.action == "update"
    assert outcome.page_id == seeded_id
    updated_key = fake.pages[seeded_id]["Output Key"]["rich_text"][0]["text"]["content"]
    assert updated_key.startswith("g:")


def test_gtm_output_body_children_keep_content_readable() -> None:
    children = gtm_output_body_children(_output())
    assert children[0]["type"] == "heading_1"
    assert children[2]["paragraph"]["rich_text"][0]["text"]["content"] == "Mensaje completo"


def test_repeated_gtm_output_upsert_updates_existing_page() -> None:
    fake = StatefulFakeOutputClient()
    first = upsert_gtm_output("db_outputs", _output(), fake)
    second = upsert_gtm_output("db_outputs", _output(content="# Outreach\n\nMensaje actualizado"), fake)

    assert first.action == "create"
    assert second.action == "update"
    assert second.page_id == first.page_id
    assert len(fake.creates) == 1
    assert len(fake.updates) == 1
    assert len(fake.pages) == 1

    props = fake.pages[first.page_id]
    assert "Mensaje actualizado" in props["Content"]["rich_text"][0]["text"]["content"]
    assert fake.children[first.page_id]
