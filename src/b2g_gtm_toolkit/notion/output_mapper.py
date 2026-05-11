from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterable, List

from b2g_gtm_toolkit.models.gtm import GtmOutput, GtmOutputType

from .write import _relation, _rich_text, _select, _title


_CONTENT_PROPERTY_LIMIT = 1900
_RICH_TEXT_CHUNK_SIZE = 1900


def source_evidence_hash_for_output(output: GtmOutput) -> str:
    """Return a deterministic evidence hash that excludes generated content."""
    if output.source_evidence_hash:
        return output.source_evidence_hash
    evidence_parts = sorted(output.research_record_refs)
    if not evidence_parts:
        evidence_parts = [output.opportunity_ref or "", output.target_account_ref or ""]
    payload = "|".join(part for part in evidence_parts if part) or "no-evidence"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def output_key_for_gtm_output(output: GtmOutput) -> str:
    if output.output_key:
        return output.output_key
    parts = [
        output.type.value,
        output.opportunity_ref or "no-opportunity",
        output.target_account_ref or "no-target-account",
        source_evidence_hash_for_output(output),
    ]
    return "|".join(parts)


def default_channel_for_type(output_type: GtmOutputType) -> str:
    if output_type == GtmOutputType.outreach:
        return "email"
    if output_type == GtmOutputType.meeting_prep:
        return "meeting"
    return "proposal"


def gtm_output_properties(output: GtmOutput) -> Dict[str, Any]:
    source_evidence_hash = source_evidence_hash_for_output(output)
    output_key = output.output_key or output_key_for_gtm_output(output)
    props: Dict[str, Any] = {
        "Title": _title(output.title),
        "Type": _select(output.type.value),
        "Output Key": _rich_text(output_key),
        "Source Evidence Hash": _rich_text(source_evidence_hash),
        "Stage": _select(output.stage),
        "Channel": _select(output.channel or default_channel_for_type(output.type)),
        "Content": _rich_text(_truncate_content_property(output.content)),
        "Source Summary": _rich_text(output.source_summary),
        "Approval Status": _select(output.approval_status.value if output.approval_status else None),
    }
    if output.owner_ref:
        props["Owner"] = _relation([output.owner_ref])
    if output.target_account_ref:
        props["Target Account"] = _relation([output.target_account_ref])
    if output.opportunity_ref:
        props["Opportunity"] = _relation([output.opportunity_ref])
    if output.research_record_refs:
        props["Research Records"] = _relation(output.research_record_refs)
    return props


def dedupe_filter_for_gtm_output(output: GtmOutput) -> Dict[str, Any]:
    return {"property": "Output Key", "rich_text": {"equals": output_key_for_gtm_output(output)}}


def gtm_output_body_children(output: GtmOutput) -> List[Dict[str, Any]]:
    children: List[Dict[str, Any]] = []
    for raw_line in output.content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            children.append(_block("heading_1", line[2:].strip()))
        elif line.startswith("## "):
            children.append(_block("heading_2", line[3:].strip()))
        elif line.startswith("### "):
            children.append(_block("heading_3", line[4:].strip()))
        elif line.startswith("- "):
            children.append(_block("bulleted_list_item", line[2:].strip()))
        else:
            children.append(_block("paragraph", line))
    return children


def _truncate_content_property(content: str) -> str:
    if len(content) <= _CONTENT_PROPERTY_LIMIT:
        return content
    return content[: _CONTENT_PROPERTY_LIMIT - 3].rstrip() + "..."


def _block(block_type: str, content: str) -> Dict[str, Any]:
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": list(_rich_text_chunks(content))},
    }


def _rich_text_chunks(content: str) -> Iterable[Dict[str, Any]]:
    text = content or ""
    if not text:
        yield {"type": "text", "text": {"content": ""}}
        return
    for idx in range(0, len(text), _RICH_TEXT_CHUNK_SIZE):
        yield {"type": "text", "text": {"content": text[idx : idx + _RICH_TEXT_CHUNK_SIZE]}}
