from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from b2g_gtm_toolkit.models.business import BusinessProfile
from b2g_gtm_toolkit.models.secop import SecopResearchInput
from b2g_gtm_toolkit.secop.research import default_offline_fixtures, run_research

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"
SCHEMA_PATH = ROOT / "schemas" / "secop-research-output.schema.json"


def test_business_profile_fixture_validates() -> None:
    raw = json.loads((FIXTURES / "business-profile.sample.json").read_text(encoding="utf-8"))
    BusinessProfile.model_validate(raw)


def test_mvp_smoke_offline_research_to_jsonl(tmp_path: Path) -> None:
    raw_input = json.loads(
        (ROOT / "examples" / "secop-research-input.json").read_text(encoding="utf-8")
    )
    input_data = SecopResearchInput.model_validate(raw_input)

    fixtures = default_offline_fixtures(FIXTURES / "secop")
    run = run_research(
        input_data,
        output_root=tmp_path / "runs",
        offline_fixtures=fixtures,
    )

    assert run.run_dir.exists(), "run dir should be created"
    assert run.jsonl_path.exists(), "jsonl path should exist"
    assert run.manifest_path.exists(), "manifest path should exist"

    lines = [
        line for line in run.jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(lines) > 0, "jsonl must be non-empty"
    assert run.deduped_count == len(lines)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    record_schema = schema["$defs"]["research_record"]
    validator = Draft202012Validator(record_schema)
    for idx, line in enumerate(lines):
        record = json.loads(line)
        errors = sorted(validator.iter_errors(record), key=lambda e: e.path)
        assert not errors, f"line {idx} schema errors: {[e.message for e in errors]}"
