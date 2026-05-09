from __future__ import annotations

import json
from pathlib import Path

from b2g_gtm_toolkit.outputs import (
    build_meeting_prep_context,
    build_outreach_context,
    build_proposal_context,
)
from b2g_gtm_toolkit.outputs.render import render

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "opportunity.sample.json"


def _load_fixture():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return data["opportunity"], data["account"], data["research"]


def _has_secop_reference(context: dict, markdown: str) -> bool:
    refs = context.get("source_refs") or []
    if not refs:
        return False
    for ref in refs:
        for key in ("source_record_id", "process_id", "contract_id"):
            value = ref.get(key)
            if value and str(value) in markdown:
                return True
    return False


def test_outreach_output_references_secop_source() -> None:
    opportunity, account, research = _load_fixture()
    ctx = build_outreach_context(opportunity, account, research)
    assert ctx["source_refs"], "outreach context must include SECOP source_refs"
    md = render("outreach.md", ctx)
    assert _has_secop_reference(ctx, md)


def test_meeting_prep_output_references_secop_source() -> None:
    opportunity, account, research = _load_fixture()
    ctx = build_meeting_prep_context(opportunity, account, research)
    assert ctx["source_refs"], "meeting prep context must include SECOP source_refs"
    md = render("meeting-prep.md", ctx)
    assert _has_secop_reference(ctx, md)


def test_proposal_output_references_secop_source() -> None:
    opportunity, account, research = _load_fixture()
    ctx = build_proposal_context(opportunity, account, research)
    assert ctx["source_refs"], "proposal context must include SECOP source_refs"
    md = render("proposal-brief.md", ctx)
    assert _has_secop_reference(ctx, md)
