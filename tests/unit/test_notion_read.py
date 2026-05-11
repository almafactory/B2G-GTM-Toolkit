from __future__ import annotations

from typing import Any, Dict, Optional

from b2g_gtm_toolkit.notion.read import (
    resolve_opportunity_input,
    resolve_target_account_input,
)
from b2g_gtm_toolkit.outputs import build_outreach_context


DB_IDS = {
    "B2G SECOP Research": "db_secop",
    "B2G GTM Outputs": "db_outputs",
}


class FakeNotionReader:
    def __init__(self, pages: Dict[str, Dict[str, Any]], page_databases: Dict[str, str]) -> None:
        self.pages = pages
        self.page_databases = page_databases
        self.retrieved_pages: list[str] = []
        self.queries: list[dict[str, Any]] = []

    def retrieve_page(self, page_id: str) -> Dict[str, Any]:
        self.retrieved_pages.append(page_id)
        return self.pages[page_id]

    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]):
        self.queries.append({"database_id": database_id, "filter": filter})
        return [
            page
            for page_id, page in self.pages.items()
            if self.page_databases.get(page_id) == database_id and _matches_filter(page, filter)
        ]


def _matches_filter(page: Dict[str, Any], filter: Optional[Dict[str, Any]]) -> bool:
    if not filter:
        return True
    if "or" in filter:
        return any(_matches_filter(page, clause) for clause in filter["or"])
    prop = filter["property"]
    if "relation" in filter:
        wanted = filter["relation"]["contains"]
        relation_ids = [item["id"] for item in page["properties"].get(prop, {}).get("relation", [])]
        return wanted in relation_ids
    return False


def _page(page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": page_id, "properties": properties}


def _title(value: str) -> Dict[str, Any]:
    return {"title": [{"type": "text", "plain_text": value, "text": {"content": value}}]}


def _rich_text(value: str) -> Dict[str, Any]:
    return {"rich_text": [{"type": "text", "plain_text": value, "text": {"content": value}}]}


def _select(value: str) -> Dict[str, Any]:
    return {"select": {"name": value}}


def _number(value: float) -> Dict[str, Any]:
    return {"number": value}


def _url(value: str) -> Dict[str, Any]:
    return {"url": value}


def _date(value: str) -> Dict[str, Any]:
    return {"date": {"start": value}}


def _relation(*page_ids: str) -> Dict[str, Any]:
    return {"relation": [{"id": page_id} for page_id in page_ids]}


def _multi_select(*values: str) -> Dict[str, Any]:
    return {"multi_select": [{"name": value} for value in values]}


def _account_page(name: str = "Alcaldia Notion") -> Dict[str, Any]:
    return _page(
        "account-1",
        {
            "Name": _title(name),
            "Entity Type": _select("alcaldia"),
            "NIT": _rich_text("890106291"),
            "Department": _select("Atlantico"),
            "Municipality": _rich_text("Soledad"),
            "Fit Score": _number(91),
        },
    )


def _research_page(page_id: str = "research-1") -> Dict[str, Any]:
    return _page(
        page_id,
        {
            "Object": _title("Servicios de software financiero"),
            "Source Platform": _select("SECOP_II"),
            "Source Record ID": _rich_text("SECOP-NOTION-1"),
            "Source URL": _url("https://example.test/secop/1"),
            "Process ID": _rich_text("PROC-NOTION-1"),
            "Buyer Name": _rich_text("MUNICIPIO DE SOLEDAD"),
            "Buyer NIT": _rich_text("890106291"),
            "Modality": _select("licitacion_publica"),
            "Status": _select("open"),
            "Contract Value": _number(2500000000),
            "Publication Date": _date("2026-05-01"),
            "UNSPSC Codes": _multi_select("43231500"),
            "Target Account": _relation("account-1"),
        },
    )


def test_opportunity_read_uses_notion_values_not_conflicting_local_data() -> None:
    local_stale_data = {
        "opportunity": {"title": "Oportunidad local obsoleta"},
        "account": {"name": "Cuenta local obsoleta"},
        "research": [{"source_record_id": "STALE-LOCAL"}],
    }
    fake = FakeNotionReader(
        pages={
            "opportunity-1": _page(
                "opportunity-1",
                {
                    "Title": _title("Modernizacion ERP desde Notion"),
                    "Status": _select("open"),
                    "Estimated Value": _number(3200000000),
                    "Target Account": _relation("account-1"),
                    "Research Records": _relation("research-1"),
                },
            ),
            "account-1": _account_page("Alcaldia de Soledad desde Notion"),
            "research-1": _research_page(),
            "output-1": _page(
                "output-1",
                {
                    "Title": _title("Outreach previo"),
                    "Type": _select("outreach"),
                    "Opportunity": _relation("opportunity-1"),
                    "Target Account": _relation("account-1"),
                },
            ),
        },
        page_databases={"research-1": "db_secop", "output-1": "db_outputs"},
    )

    resolved = resolve_opportunity_input(
        opportunity_page_id="opportunity-1",
        database_ids=DB_IDS,
        client=fake,
    )
    context = build_outreach_context(*resolved.builder_args())

    assert local_stale_data["account"]["name"] not in context["account_name"]
    assert resolved.opportunity["title"] == "Modernizacion ERP desde Notion"
    assert resolved.account["name"] == "Alcaldia de Soledad desde Notion"
    assert resolved.research[0]["source_record_id"] == "SECOP-NOTION-1"
    assert resolved.prior_outputs[0]["title"] == "Outreach previo"
    assert fake.retrieved_pages == ["opportunity-1", "account-1", "research-1"]


def test_opportunity_read_queries_account_research_when_relation_is_empty() -> None:
    fake = FakeNotionReader(
        pages={
            "opportunity-1": _page(
                "opportunity-1",
                {
                    "Title": _title("Oportunidad sin relacion directa"),
                    "Target Account": _relation("account-1"),
                    "Research Records": _relation(),
                },
            ),
            "account-1": _account_page(),
            "research-1": _research_page(),
        },
        page_databases={"research-1": "db_secop"},
    )

    resolved = resolve_opportunity_input(
        opportunity_page_id="opportunity-1",
        database_ids=DB_IDS,
        client=fake,
    )

    assert [item["source_record_id"] for item in resolved.research] == ["SECOP-NOTION-1"]
    assert fake.queries[0]["database_id"] == "db_secop"
    assert fake.queries[0]["filter"] == {"property": "Target Account", "relation": {"contains": "account-1"}}


def test_target_account_read_resolves_related_research_without_opportunity() -> None:
    fake = FakeNotionReader(
        pages={
            "account-1": _account_page("Alcaldia de Soledad"),
            "research-1": _research_page(),
        },
        page_databases={"research-1": "db_secop"},
    )

    resolved = resolve_target_account_input(
        target_account_page_id="account-1",
        database_ids=DB_IDS,
        client=fake,
    )

    assert resolved.opportunity["title"] == "Alcaldia de Soledad"
    assert resolved.account["location"] == "Soledad, Atlantico"
    assert resolved.research[0]["process_id"] == "PROC-NOTION-1"
