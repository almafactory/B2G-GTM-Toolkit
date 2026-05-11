"""Normalization helpers for Notion dedupe filters and comparisons only."""

from __future__ import annotations

import re
from typing import Optional

from b2g_gtm_toolkit.utils.ids import normalize_text as _accent_fold_normalize

_WS_COLLAPSE = re.compile(r"\s+")

# Canonical target-account dedupe: normalized NIT (digits-only) equals if present,
# otherwise normalized entity name (+ optional Municipality when provided).


def collapse_whitespace(value: Optional[str]) -> str:
    return _WS_COLLAPSE.sub(" ", (value or "").strip())


def nit_digits_normalized(value: Optional[str]) -> str:
    """Colombian-style NIT: compare on digits only (hyphens/formatting-insensitive)."""
    return re.sub(r"\D+", "", value or "")


def municipality_normalized(value: Optional[str]) -> str:
    if not value:
        return ""
    return _accent_fold_normalize(value)


def entity_name_normalized(*, normalized_name: Optional[str], display_name: str) -> str:
    """Accent-fold / case-fold entity label used for Normalized Name + dedupe (not necessarily display)."""
    base = normalized_name if (normalized_name and normalized_name.strip()) else display_name
    return _accent_fold_normalize(base or "")

