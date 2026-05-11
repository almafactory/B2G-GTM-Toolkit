"""Unit coverage for notion dedupe normalization and duplicate repair grouping."""

from __future__ import annotations

from typing import Any, Dict, List


from b2g_gtm_toolkit.models.gtm import TargetAccount
from b2g_gtm_toolkit.notion.dedupe_norm import entity_name_normalized, nit_digits_normalized
from b2g_gtm_toolkit.notion.target_account_repair import apply_duplicate_merge, find_duplicate_groups


def test_nit_digits_strip_non_digits() -> None:
    assert nit_digits_normalized("890106291-9") == "8901062919"


def test_entity_name_normalized_folds_accents_for_dedupe() -> None:
    a = entity_name_normalized(normalized_name=None, display_name="Alcaldía")
    b = entity_name_normalized(normalized_name=None, display_name="Alcaldia")
    assert a == b == "alcaldia"


def test_target_account_match_filter_contains_nit_arm() -> None:
    from b2g_gtm_toolkit.notion.write import target_account_match_filter

    account = TargetAccount(name=" Municipio X ", municipality="Barranquilla ", nit="800.123")
    filt = target_account_match_filter(account)
    assert isinstance(filt, dict) and "or" in filt
    nit_clauses = [c for c in filt["or"] if c.get("property") == "NIT"]
    assert nit_clauses and nit_clauses[0]["rich_text"]["equals"] == "800123"


def _simple_page(pid: str, title: str, nit: str, municipality: str) -> Dict[str, Any]:
    return {
        "id": pid,
        "created_time": "2026-01-01T12:00:00.000Z",
        "properties": {
            "Name": {"title": [{"plain_text": title, "type": "text", "text": {"content": title}}]},
            "Normalized Name": {
                "rich_text": [{"plain_text": "x", "type": "text", "text": {"content": "unused"}}],
            },
            "Municipality": {
                "rich_text": [{"plain_text": municipality, "type": "text", "text": {"content": municipality}}],
            },
            "Department": {"select": {"name": "ATL"}},
            "NIT": {"rich_text": [{"plain_text": nit, "type": "text", "text": {"content": nit}}]},
            "Entity Type": {"select": {"name": "alcaldia"}},
        },
    }


def test_find_duplicate_groups_by_nit() -> None:
    pages = [
        _simple_page("p1", "A", nit="890", municipality="Soledad"),
        _simple_page("p2", "B", nit="890", municipality="Otros"),
    ]
    groups = find_duplicate_groups(pages)
    assert len(groups) == 1
    canon = groups[0]["canonical_page_id"]
    dups = set(groups[0]["duplicate_page_ids"]) | {canon}
    assert dups == {"p1", "p2"}


def test_apply_duplicate_merge_updates_relations() -> None:
    class _Client:
        def __init__(self) -> None:
            self.updated: List[Dict[str, Any]] = []

        def update_page(self, page_id: str, properties):
            self.updated.append({"page_id": page_id, "properties": properties})

        def archive_page(self, page_id: str):
            return {"id": page_id}

    def fake_fetch(ds: str, filt: Dict[str, Any]):
        if filt["property"] == "Target Account" and ds == "secop":
            return [{"id": "s1"}, {"id": "s2"}]
        return [{"id": "g1"}]

    client = _Client()
    groups = [{"canonical_page_id": "canonical1", "duplicate_page_ids": ["dup1"]}]
    res = apply_duplicate_merge(
        duplicate_groups=groups,
        client=client,
        secop_database_id="secop",
        gtm_outputs_database_id="gtm",
        fetch_with_filter=fake_fetch,
        archive_duplicates=True,
    )
    assert client.updated == [
        {"page_id": "s1", "properties": {"Target Account": {"relation": [{"id": "canonical1"}]}}},
        {"page_id": "s2", "properties": {"Target Account": {"relation": [{"id": "canonical1"}]}}},
        {"page_id": "g1", "properties": {"Target Account": {"relation": [{"id": "canonical1"}]}}},
    ]
    assert res.relinked_secop == 2
    assert res.relinked_outputs == 1
    assert res.archived_pages == 1
