from __future__ import annotations

from datetime import datetime, timezone

import pytest

from b2g_gtm_toolkit.utils.ids import hash_payload, normalize_text, now_utc, stable_id


def test_normalize_text_lowercase_and_strips_accents() -> None:
    assert normalize_text("Alcaldía  de  Medellín") == "alcaldia de medellin"


def test_normalize_text_handles_none_and_empty() -> None:
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""


def test_stable_id_deterministic() -> None:
    a = stable_id("Alcaldía", "Medellín", "12345")
    b = stable_id("Alcaldía", "Medellín", "12345")
    assert a == b
    assert "-" in a


def test_stable_id_changes_with_inputs() -> None:
    a = stable_id("Alcaldía", "Medellín")
    b = stable_id("Alcaldía", "Cali")
    assert a != b


def test_stable_id_requires_parts() -> None:
    with pytest.raises(ValueError):
        stable_id()
    with pytest.raises(ValueError):
        stable_id("", None)


def test_hash_payload_canonical() -> None:
    h1 = hash_payload({"a": 1, "b": [2, 3]})
    h2 = hash_payload({"b": [2, 3], "a": 1})
    assert h1 == h2
    assert len(h1) == 64


def test_hash_payload_changes_on_modification() -> None:
    assert hash_payload({"a": 1}) != hash_payload({"a": 2})


def test_hash_payload_supports_datetime() -> None:
    h = hash_payload({"ts": datetime(2026, 5, 9, tzinfo=timezone.utc)})
    assert isinstance(h, str)


def test_now_utc_is_timezone_aware() -> None:
    n = now_utc()
    assert n.tzinfo is not None
