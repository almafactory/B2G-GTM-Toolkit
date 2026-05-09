from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any


_SLUG_RE = re.compile(r"[^a-z0-9]+")
_WS_RE = re.compile(r"\s+")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def normalize_text(s: str) -> str:
    if s is None:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(s))
    no_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    lowered = no_accents.lower().strip()
    return _WS_RE.sub(" ", lowered)


def _slugify(s: str) -> str:
    norm = normalize_text(s)
    slug = _SLUG_RE.sub("-", norm).strip("-")
    return slug


def hash_payload(obj: Any) -> str:
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def stable_id(*parts: Any) -> str:
    cleaned = [str(p) for p in parts if p is not None and str(p) != ""]
    if not cleaned:
        raise ValueError("stable_id requires at least one non-empty part")
    slug_source = "-".join(_slugify(p) for p in cleaned if _slugify(p))
    digest = hashlib.sha256("|".join(cleaned).encode("utf-8")).hexdigest()[:12]
    if slug_source:
        slug_truncated = slug_source[:48].strip("-")
        return f"{slug_truncated}-{digest}"
    return digest
