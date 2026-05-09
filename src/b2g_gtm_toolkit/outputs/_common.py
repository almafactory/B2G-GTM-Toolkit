from __future__ import annotations

from typing import Any, Dict, List, Optional


def _g(d: Optional[Dict[str, Any]], *keys: str, default: Any = None) -> Any:
    if not d:
        return default
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default


def _format_cop(value: Optional[float]) -> str:
    if value is None:
        return "s/d"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "s/d"
    return f"COP {v:,.0f}".replace(",", ".")


def _location(account: Dict[str, Any]) -> str:
    return (
        account.get("location")
        or account.get("municipality")
        or account.get("department")
        or "su jurisdicción"
    )


def _sort_research(research: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def key(r: Dict[str, Any]):
        return (
            r.get("award_date") or r.get("publication_date") or "",
            r.get("source_record_id") or "",
        )
    return sorted(research or [], key=key, reverse=True)


def build_source_refs(research: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    refs: List[Dict[str, Any]] = []
    for r in _sort_research(research)[:limit]:
        refs.append(
            {
                "source_record_id": r.get("source_record_id"),
                "process_id": r.get("process_id"),
                "contract_id": r.get("contract_id"),
                "object": r.get("object"),
                "value": r.get("contract_value"),
                "value_formatted": _format_cop(r.get("contract_value")),
                "modality": r.get("modality"),
                "status": r.get("status"),
                "award_date": str(r.get("award_date")) if r.get("award_date") else None,
                "publication_date": str(r.get("publication_date")) if r.get("publication_date") else None,
                "url": r.get("source_url"),
                "buyer_name": r.get("buyer_name"),
            }
        )
    return refs


def average_value(research: List[Dict[str, Any]]) -> Optional[float]:
    vals = [r.get("contract_value") for r in (research or []) if r.get("contract_value") is not None]
    if not vals:
        return None
    try:
        return sum(float(v) for v in vals) / len(vals)
    except (TypeError, ValueError):
        return None
