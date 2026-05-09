from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from b2g_gtm_toolkit.models.secop import ResearchTaskType, SecopResearchInput
from b2g_gtm_toolkit.secop.research import default_offline_fixtures, run_research


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "secop-research-output.schema.json"
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "secop"


def test_jsonl_records_match_schema(tmp_path: Path):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    record_schema = schema["$defs"]["research_record"]
    validator = Draft202012Validator(record_schema)

    input_data = SecopResearchInput(
        task_type=ResearchTaskType.opportunity_discovery,
        datasets=["secop_ii_procesos", "secop_ii_contratos"],
        result_limit=50,
        page_size=50,
    )
    fixtures = default_offline_fixtures(FIXTURE_DIR)
    run = run_research(input_data, output_root=tmp_path, offline_fixtures=fixtures)

    lines = [l for l in run.jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines, "JSONL output is empty"
    for line in lines:
        record = json.loads(line)
        errors = sorted(validator.iter_errors(record), key=lambda e: e.path)
        assert not errors, f"Schema errors: {[e.message for e in errors]}"
