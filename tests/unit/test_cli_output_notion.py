from __future__ import annotations

from typing import Any, Dict, Optional

from typer.testing import CliRunner

from b2g_gtm_toolkit import cli


class FakeOutputWorkflowClient:
    def __init__(self) -> None:
        self.pages = {
            "opportunity-1": _page(
                "opportunity-1",
                {
                    "Title": _title("Modernizacion ERP"),
                    "Target Account": _relation("account-1"),
                    "Research Records": _relation("research-1"),
                },
            ),
            "account-1": _page(
                "account-1",
                {
                    "Name": _title("Alcaldia de Soledad"),
                    "Entity Type": _select("alcaldia"),
                    "Department": _select("Atlantico"),
                    "Municipality": _rich_text("Soledad"),
                },
            ),
            "research-1": _page(
                "research-1",
                {
                    "Object": _title("Servicios de software financiero"),
                    "Source Platform": _select("SECOP_II"),
                    "Source Record ID": _rich_text("SECOP-1"),
                    "Process ID": _rich_text("PROC-1"),
                    "Buyer Name": _rich_text("MUNICIPIO DE SOLEDAD"),
                    "Contract Value": {"number": 1200000000},
                    "Target Account": _relation("account-1"),
                },
            ),
        }
        self.page_databases = {"research-1": "db_secop"}
        self.creates: list[dict[str, Any]] = []
        self.updates: list[dict[str, Any]] = []
        self.children: dict[str, list[dict[str, Any]]] = {}

    def retrieve_page(self, page_id: str) -> Dict[str, Any]:
        return self.pages[page_id]

    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]):
        return [
            page
            for page_id, page in self.pages.items()
            if self.page_databases.get(page_id) == database_id and _matches_filter(page, filter)
        ]

    def create_page(self, database_id: str, properties: Dict[str, Any], children=None):
        page_id = f"output-{len(self.creates) + 1}"
        self.creates.append({"database_id": database_id, "properties": properties, "children": children or []})
        self.pages[page_id] = {"id": page_id, "properties": properties}
        self.page_databases[page_id] = database_id
        self.children[page_id] = children or []
        return {"id": page_id}

    def update_page(self, page_id: str, properties: Dict[str, Any]):
        self.updates.append({"page_id": page_id, "properties": properties})
        self.pages[page_id] = {"id": page_id, "properties": properties}
        return {"id": page_id}

    def append_page_children(self, page_id: str, children):
        self.children.setdefault(page_id, []).extend(children)
        return {"id": page_id}


def _page(page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": page_id, "properties": properties}


def _title(value: str) -> Dict[str, Any]:
    return {"title": [{"type": "text", "plain_text": value, "text": {"content": value}}]}


def _rich_text(value: str) -> Dict[str, Any]:
    return {"rich_text": [{"type": "text", "plain_text": value, "text": {"content": value}}]}


def _select(value: str) -> Dict[str, Any]:
    return {"select": {"name": value}}


def _relation(*page_ids: str) -> Dict[str, Any]:
    return {"relation": [{"id": page_id} for page_id in page_ids]}


def _matches_filter(page: Dict[str, Any], filter: Optional[Dict[str, Any]]) -> bool:
    if not filter:
        return True
    if "or" in filter:
        return any(_matches_filter(page, clause) for clause in filter["or"])
    if "and" in filter:
        return all(_matches_filter(page, clause) for clause in filter["and"])
    prop = filter["property"]
    if "relation" in filter:
        wanted = filter["relation"]["contains"]
        relation_ids = [item["id"] for item in page["properties"].get(prop, {}).get("relation", [])]
        return wanted in relation_ids
    if "rich_text" in filter:
        items = page["properties"].get(prop, {}).get("rich_text", [])
        current = items[0]["text"]["content"] if items else None
        return current == filter["rich_text"]["equals"]
    return False


def test_output_create_writes_and_reuses_notion_output_page(monkeypatch) -> None:
    fake = FakeOutputWorkflowClient()
    monkeypatch.setattr(cli, "_build_notion_client", lambda: (fake, True))
    monkeypatch.setattr(
        cli,
        "_database_ids_for_names",
        lambda names, client: {"B2G SECOP Research": "db_secop", "B2G GTM Outputs": "db_outputs"},
    )
    runner = CliRunner()

    first = runner.invoke(
        cli.app,
        ["output", "create", "--type", "outreach", "--opportunity-page", "opportunity-1", "--to-notion", "--apply"],
    )
    second = runner.invoke(
        cli.app,
        ["output", "create", "--type", "outreach", "--opportunity-page", "opportunity-1", "--to-notion", "--apply"],
    )

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert len(fake.creates) == 1
    assert len(fake.updates) == 1

    output_props = fake.pages["output-1"]["properties"]
    assert output_props["Target Account"]["relation"][0]["id"] == "account-1"
    assert output_props["Opportunity"]["relation"][0]["id"] == "opportunity-1"
    assert output_props["Research Records"]["relation"][0]["id"] == "research-1"
    assert "Alcaldia de Soledad" in output_props["Content"]["rich_text"][0]["text"]["content"]
    assert fake.children["output-1"]
