from __future__ import annotations


def test_cli_known_database_ids_loads_local_dotenv(tmp_path, monkeypatch) -> None:
    from b2g_gtm_toolkit import cli

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NOTION_DB_B2G_OWNERS", raising=False)
    (tmp_path / ".env").write_text("NOTION_DB_B2G_OWNERS=owners-from-dotenv\n", encoding="utf-8")

    ids = cli._known_database_ids()

    assert ids["B2G Owners"] == "owners-from-dotenv"


def test_cli_dotenv_does_not_override_exported_values(tmp_path, monkeypatch) -> None:
    from b2g_gtm_toolkit import cli

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NOTION_DB_B2G_OWNERS", "owners-from-shell")
    (tmp_path / ".env").write_text("NOTION_DB_B2G_OWNERS=owners-from-dotenv\n", encoding="utf-8")

    ids = cli._known_database_ids()

    assert ids["B2G Owners"] == "owners-from-shell"
