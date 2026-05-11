from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from typer.testing import CliRunner

from b2g_gtm_toolkit import cli


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "secop"
NOTION_PAGE_ID = "12345678-1234-1234-1234-123456789abc"


class FakeResearchNotionClient:
    def __init__(self) -> None:
        self.queries: list[dict[str, Any]] = []
        self.creates: list[dict[str, Any]] = []
        self.updates: list[dict[str, Any]] = []

    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]):
        self.queries.append({"database_id": database_id, "filter": filter})
        return []

    def create_page(self, database_id: str, properties: Dict[str, Any]):
        self.creates.append({"database_id": database_id, "properties": properties})
        return {"id": f"research-{len(self.creates)}"}

    def update_page(self, page_id: str, properties: Dict[str, Any]):
        self.updates.append({"page_id": page_id, "properties": properties})
        return {"id": page_id}


def _write_input(tmp_path: Path, target_account_ref: Optional[str] = None) -> Path:
    payload: dict[str, Any] = {
        "task_type": "opportunity_discovery",
        "entity_nits": ["890905211"],
        "datasets": ["secop_ii_procesos"],
        "result_limit": 10,
        "page_size": 10,
    }
    if target_account_ref:
        payload["target_account_ref"] = target_account_ref
    path = tmp_path / "secop-input.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_research_write_through_calls_notion_upsert(monkeypatch, tmp_path: Path) -> None:
    fake = FakeResearchNotionClient()
    monkeypatch.setenv("NOTION_TOKEN", "test-token")
    monkeypatch.setattr(cli, "_load_cli_env", lambda *args, **kwargs: False)
    monkeypatch.setattr(cli, "_build_notion_client", lambda: (fake, True))
    monkeypatch.setattr(
        cli,
        "_database_ids_for_names",
        lambda names, client: {"B2G SECOP Research": "db_secop"},
    )
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "secop",
            "research",
            "--input",
            str(_write_input(tmp_path)),
            "--offline",
            "--output-root",
            str(tmp_path / "runs"),
            "--fixtures-dir",
            str(FIXTURE_DIR),
            "--to-notion",
            "--apply",
        ],
    )

    assert result.exit_code == 0, result.output
    assert fake.queries
    assert fake.creates
    assert "Notion escrito:" in result.output
    assert "investigacion SECOP completada" in result.output


def test_research_write_through_sets_target_relation_for_page_id(monkeypatch, tmp_path: Path) -> None:
    fake = FakeResearchNotionClient()
    monkeypatch.setenv("NOTION_TOKEN", "test-token")
    monkeypatch.setattr(cli, "_load_cli_env", lambda *args, **kwargs: False)
    monkeypatch.setattr(cli, "_build_notion_client", lambda: (fake, True))
    monkeypatch.setattr(
        cli,
        "_database_ids_for_names",
        lambda names, client: {"B2G SECOP Research": "db_secop"},
    )
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "secop",
            "research",
            "--input",
            str(_write_input(tmp_path, NOTION_PAGE_ID)),
            "--offline",
            "--output-root",
            str(tmp_path / "runs"),
            "--fixtures-dir",
            str(FIXTURE_DIR),
            "--to-notion",
            "--apply",
        ],
    )

    assert result.exit_code == 0, result.output
    assert fake.creates
    assert fake.creates[0]["properties"]["Target Account"]["relation"][0]["id"] == NOTION_PAGE_ID
    assert "Target Account: relacionado usando el page id provisto." in result.output


def test_research_preview_to_notion_does_not_write(monkeypatch, tmp_path: Path) -> None:
    fake = FakeResearchNotionClient()
    monkeypatch.setattr(cli, "_build_notion_client", lambda: (fake, True))
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "secop",
            "research",
            "--input",
            str(_write_input(tmp_path, "Alcaldia de Soledad")),
            "--offline",
            "--output-root",
            str(tmp_path / "runs"),
            "--fixtures-dir",
            str(FIXTURE_DIR),
            "--to-notion",
        ],
    )

    assert result.exit_code == 0, result.output
    assert fake.queries == []
    assert fake.creates == []
    assert fake.updates == []
    assert "Notion preview: nada fue escrito." in result.output
    assert "Target Account: referencia no resuelta" in result.output


def test_research_write_through_does_not_link_unresolved_target_ref(monkeypatch, tmp_path: Path) -> None:
    fake = FakeResearchNotionClient()
    monkeypatch.setenv("NOTION_TOKEN", "test-token")
    monkeypatch.setattr(cli, "_load_cli_env", lambda *args, **kwargs: False)
    monkeypatch.setattr(cli, "_build_notion_client", lambda: (fake, True))
    monkeypatch.setattr(
        cli,
        "_database_ids_for_names",
        lambda names, client: {
            "B2G SECOP Research": "db_secop",
            "B2G Target Accounts": "db_accounts",
        },
    )
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "secop",
            "research",
            "--input",
            str(_write_input(tmp_path, "local-account-ref")),
            "--offline",
            "--output-root",
            str(tmp_path / "runs"),
            "--fixtures-dir",
            str(FIXTURE_DIR),
            "--to-notion",
            "--apply",
        ],
    )

    assert result.exit_code == 0, result.output
    assert fake.creates
    assert "Target Account" not in fake.creates[0]["properties"]
    assert "Target Account: referencia no resuelta" in result.output
