from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

TEMPLATES_DIR = (
    Path(__file__).resolve().parents[3] / "skills" / "b2g-output-workflows" / "templates"
)


def _bullets(items: List[str], indent: str = "- ") -> str:
    if not items:
        return "_(sin elementos)_"
    return "\n".join(f"{indent}{item}" for item in items)


def _source_refs_block(source_refs: List[Dict[str, Any]]) -> str:
    if not source_refs:
        return "_(sin referencias SECOP disponibles)_"
    lines: List[str] = []
    for ref in source_refs:
        ref_id = ref.get("process_id") or ref.get("contract_id") or ref.get("source_record_id") or "s/d"
        obj = ref.get("object") or "s/d"
        val = ref.get("value_formatted") or "s/d"
        modality = ref.get("modality") or "s/d"
        date = ref.get("award_date") or ref.get("publication_date") or "s/d"
        url = ref.get("url")
        url_part = f" ([fuente]({url}))" if url else ""
        lines.append(f"- `{ref_id}` — {obj} — {modality} — {val} — {date}{url_part}")
    return "\n".join(lines)


def _history_block(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "_(sin historial SECOP disponible)_"
    lines: List[str] = []
    for it in items:
        lines.append(
            f"- `{it.get('ref_id') or 's/d'}` — {it.get('object') or 's/d'} — "
            f"{it.get('modality') or 's/d'} — {it.get('value_formatted') or 's/d'} — {it.get('date') or 's/d'}"
        )
    return "\n".join(lines)


def render(template_name: str, context: Dict[str, Any]) -> str:
    template_path = TEMPLATES_DIR / template_name
    text = template_path.read_text(encoding="utf-8")

    rendered_blocks: Dict[str, str] = {
        "subject_options_block": _bullets(context.get("subject_options", []) or []),
        "opening_lines_block": _bullets(context.get("opening_lines", []) or []),
        "value_props_block": _bullets(context.get("value_props", []) or []),
        "key_objections_block": _bullets(context.get("key_objections", []) or []),
        "talking_points_block": _bullets(context.get("talking_points", []) or []),
        "business_case_summary_block": _bullets(context.get("business_case_summary", []) or []),
        "recent_secop_history_block": _history_block(context.get("recent_secop_history", []) or []),
        "evidence_block": _history_block(context.get("evidence_block", []) or []),
        "source_refs_block": _source_refs_block(context.get("source_refs", []) or []),
    }

    attendees = context.get("attendees") or {}
    buyer = attendees.get("buyer") or {}
    seller = attendees.get("seller") or {}
    rendered_blocks["buyer_entity"] = str(buyer.get("entity") or "s/d")
    rendered_blocks["buyer_role"] = str(buyer.get("expected_role") or "s/d")
    rendered_blocks["seller_role"] = str(seller.get("role") or "s/d")
    rendered_blocks["seller_objective"] = str(seller.get("objective") or "s/d")

    flat: Dict[str, Any] = {}
    for key, val in context.items():
        if isinstance(val, (str, int, float)) or val is None:
            flat[key] = "" if val is None else str(val)

    flat.update(rendered_blocks)

    out = text
    for key, val in flat.items():
        out = out.replace("{" + key + "}", str(val))
    return out
