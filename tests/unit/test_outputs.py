from __future__ import annotations

import json
from pathlib import Path

from b2g_gtm_toolkit.outputs import (
    build_meeting_prep_context,
    build_outreach_context,
    build_proposal_context,
)
from b2g_gtm_toolkit.outputs.render import render

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "opportunity.sample.json"


def _load():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return data["opportunity"], data["account"], data["research"]


def test_outreach_snapshot():
    opportunity, account, research = _load()
    ctx = build_outreach_context(opportunity, account, research)

    assert ctx["account_name"] == "Alcaldía de Medellín"
    assert ctx["entity_type"] == "alcaldía"
    assert ctx["location"] == "Medellín, Antioquia"
    assert len(ctx["subject_options"]) >= 2
    assert any("Medellín" in s or "alcaldía" in s for s in ctx["subject_options"])
    assert ctx["opening_lines"], "outreach must have at least one opening line"
    assert ctx["value_props"], "outreach must have value props"
    assert ctx["cta"]
    assert len(ctx["source_refs"]) == 3
    first_ref = ctx["source_refs"][0]
    assert first_ref["source_record_id"] == "CO1.PCCNTR.5551111"
    assert first_ref["value_formatted"].startswith("COP")


def test_meeting_prep_snapshot():
    opportunity, account, research = _load()
    ctx = build_meeting_prep_context(opportunity, account, research)

    assert ctx["account_name"] == "Alcaldía de Medellín"
    assert ctx["attendees"]["buyer"]["entity"] == "Alcaldía de Medellín"
    assert ctx["attendees"]["buyer"]["expected_role"] == "Secretario de Hacienda"
    assert ctx["attendees"]["seller"]["role"] == "Account Executive B2G"
    assert len(ctx["recent_secop_history"]) == 3
    assert ctx["recent_secop_history"][0]["ref_id"] == "PROC-2024-001"
    assert any("MEDDPICC" not in tp for tp in ctx["talking_points"])
    assert any(tp.startswith("Metric") for tp in ctx["talking_points"])
    assert ctx["key_objections"]
    assert ctx["source_refs"][0]["source_record_id"] == "CO1.PCCNTR.5551111"


def test_proposal_snapshot():
    opportunity, account, research = _load()
    ctx = build_proposal_context(opportunity, account, research)

    assert ctx["account_name"] == "Alcaldía de Medellín"
    assert "recaudo" in ctx["problem_statement"]
    assert len(ctx["evidence_block"]) == 3
    assert ctx["evidence_block"][0]["ref_id"] == "PROC-2024-001"
    assert ctx["anchor_value_formatted"].startswith("COP")
    assert ctx["anchor_value_formatted"] == "COP 1.850.000.000"
    assert any("Modalidad" in line for line in ctx["business_case_summary"])
    assert ctx["source_refs"], "proposal must cite SECOP sources"


def test_render_outreach_includes_source_ref():
    opportunity, account, research = _load()
    ctx = build_outreach_context(opportunity, account, research)
    markdown = render("outreach.md", ctx)

    assert "Alcaldía de Medellín" in markdown
    assert "CO1.PCCNTR.5551111" in markdown or "PROC-2024-001" in markdown
    assert "Referencias SECOP" in markdown


def test_render_proposal_includes_evidence():
    opportunity, account, research = _load()
    ctx = build_proposal_context(opportunity, account, research)
    markdown = render("proposal-brief.md", ctx)

    assert "Propuesta" in markdown
    assert "PROC-2024-001" in markdown
    assert "COP" in markdown


def test_empty_research_still_produces_context():
    opportunity, account, _ = _load()
    ctx = build_outreach_context(opportunity, account, [])
    assert ctx["source_refs"] == []
    assert ctx["opening_lines"], "should still produce a fallback opening"
