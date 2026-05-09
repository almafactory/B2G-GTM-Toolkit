from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from b2g_gtm_toolkit.models.secop import (
    ResearchTaskType,
    SecopNormalizedRecord,
    SecopResearchInput,
)
from b2g_gtm_toolkit.notion.write import (
    dedupe_filter_for_secop,
    secop_record_properties,
    upsert_page,
)
from b2g_gtm_toolkit.secop.research import default_offline_fixtures, run_research

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "secop"


class FakeNotionClient:
    def __init__(self) -> None:
        self.queries: List[Dict[str, Any]] = []
        self.creates: List[Dict[str, Any]] = []
        self.updates: List[Dict[str, Any]] = []

    def query_database(self, database_id: str, filter: Optional[Dict[str, Any]]):
        self.queries.append({"database_id": database_id, "filter": filter})
        return []

    def create_page(self, database_id: str, properties: Dict[str, Any]):
        self.creates.append({"database_id": database_id, "properties": properties})
        return {"id": f"page_{len(self.creates)}"}

    def update_page(self, page_id: str, properties: Dict[str, Any]):
        self.updates.append({"page_id": page_id, "properties": properties})
        return {"id": page_id}


def _load_records(jsonl: Path) -> List[SecopNormalizedRecord]:
    out: List[SecopNormalizedRecord] = []
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        prov = data.get("provenance") or {}
        if data.get("source_dataset") and not prov.get("source_dataset"):
            prov["source_dataset"] = data["source_dataset"]
            data["provenance"] = prov
        out.append(SecopNormalizedRecord.model_validate(data))
    return out


def test_research_jsonl_maps_to_notion_payloads(tmp_path: Path) -> None:
    input_data = SecopResearchInput(
        task_type=ResearchTaskType.opportunity_discovery,
        datasets=["secop_ii_procesos", "secop_ii_contratos"],
        result_limit=50,
        page_size=50,
    )
    run = run_research(
        input_data,
        output_root=tmp_path,
        offline_fixtures=default_offline_fixtures(FIXTURE_DIR),
    )

    records = _load_records(run.jsonl_path)
    assert records, "research run should produce at least one record"

    fake = FakeNotionClient()
    target_db = "B2G SECOP Research"
    results = []
    for rec in records:
        props = secop_record_properties(rec)
        dedupe = dedupe_filter_for_secop(rec)
        results.append(upsert_page(target_db, props, dedupe, client=fake))

    assert len(fake.queries) == len(records)
    assert len(fake.creates) == len(records)
    assert all(r.action == "create" for r in results)

    sample = fake.creates[0]["properties"]
    assert "Object" in sample and "title" in sample["Object"]
    assert "Source Platform" in sample and "select" in sample["Source Platform"]
    assert sample["Source Platform"]["select"]["name"] in {
        "SECOP_I",
        "SECOP_II",
        "TVEC",
        "SECOP_INTEGRATED",
        "OCDS_JSON",
    }
    assert "Source Record ID" in sample and "rich_text" in sample["Source Record ID"]

    dedupe_filter = fake.queries[0]["filter"]
    assert "and" in dedupe_filter
    keys = {clause["property"] for clause in dedupe_filter["and"]}
    assert {"Source Platform", "Source Record ID"}.issubset(keys)


def test_dry_run_without_client_returns_planned_payloads(tmp_path: Path) -> None:
    input_data = SecopResearchInput(
        task_type=ResearchTaskType.opportunity_discovery,
        datasets=["secop_ii_procesos"],
        result_limit=10,
        page_size=10,
    )
    run = run_research(
        input_data,
        output_root=tmp_path,
        offline_fixtures=default_offline_fixtures(FIXTURE_DIR),
    )
    records = _load_records(run.jsonl_path)
    assert records

    rec = records[0]
    result = upsert_page(
        "B2G SECOP Research",
        secop_record_properties(rec),
        dedupe_filter_for_secop(rec),
        client=None,
    )
    assert result.action == "dry_run_create"
    assert result.page_id is None
    assert "Source Record ID" in result.properties
