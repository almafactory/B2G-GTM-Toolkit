from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from b2g_gtm_toolkit.models.gtm import TargetAccount, TargetAccountList
from b2g_gtm_toolkit.utils.ids import stable_id

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "target-accounts.sample.json"


def _account(**overrides) -> dict:
    base = {
        "name": "Alcaldia de Pereira",
        "entity_type": "alcaldia",
        "location": "Risaralda / Pereira",
        "fit_score": 80,
    }
    base.update(overrides)
    return base


def test_sample_fixture_validates() -> None:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    account_list = TargetAccountList.model_validate(raw)

    assert len(account_list.accounts) == 4
    assert account_list.icp_id == "icp-alcaldias-cat-1-2-tic"
    names = {a.name for a in account_list.accounts}
    assert "Alcaldia de Pereira" in names
    assert "Gobernacion del Quindio" in names
    assert all(a.fit_score is None or 0 <= a.fit_score <= 100 for a in account_list.accounts)


def test_empty_account_list_rejected() -> None:
    with pytest.raises(ValidationError):
        TargetAccountList.model_validate({"accounts": []})


def test_fit_score_boundary_zero_valid() -> None:
    account_list = TargetAccountList.model_validate({"accounts": [_account(fit_score=0)]})
    assert account_list.accounts[0].fit_score == 0


def test_fit_score_boundary_hundred_valid() -> None:
    account_list = TargetAccountList.model_validate({"accounts": [_account(fit_score=100)]})
    assert account_list.accounts[0].fit_score == 100


def test_fit_score_below_zero_rejected() -> None:
    with pytest.raises(ValidationError):
        TargetAccountList.model_validate({"accounts": [_account(fit_score=-1)]})


def test_fit_score_above_hundred_rejected() -> None:
    with pytest.raises(ValidationError):
        TargetAccountList.model_validate({"accounts": [_account(fit_score=101)]})


def test_dedupe_rejects_duplicate_stable_ids() -> None:
    payload = {
        "accounts": [
            _account(name="Alcaldia de Pereira", entity_type="alcaldia", location="Risaralda / Pereira"),
            _account(name="Alcaldia de Pereira", entity_type="alcaldia", location="Risaralda / Pereira"),
        ]
    }
    with pytest.raises(ValidationError):
        TargetAccountList.model_validate(payload)


def test_different_locations_are_not_duplicates() -> None:
    payload = {
        "accounts": [
            _account(name="Alcaldia X", entity_type="alcaldia", location="Risaralda / Pereira"),
            _account(name="Alcaldia X", entity_type="alcaldia", location="Caldas / Manizales"),
        ]
    }
    account_list = TargetAccountList.model_validate(payload)
    assert len(account_list.accounts) == 2


def test_explicit_id_used_for_dedupe() -> None:
    same_id = "alcaldia-pereira-fixed-id"
    payload = {
        "accounts": [
            _account(id=same_id, name="Alcaldia de Pereira"),
            _account(id=same_id, name="Otro Nombre", entity_type="gobernacion", location="Otra"),
        ]
    }
    with pytest.raises(ValidationError):
        TargetAccountList.model_validate(payload)


def test_compute_stable_id_matches_utils() -> None:
    account = TargetAccount.model_validate(
        {"name": "Alcaldia de Pereira", "entity_type": "alcaldia", "location": "Risaralda / Pereira"}
    )
    expected = stable_id("Alcaldia de Pereira", "alcaldia", "Risaralda / Pereira")
    assert account.compute_stable_id() == expected


def test_count_metadata_must_match() -> None:
    payload = {
        "count": 5,
        "accounts": [_account()],
    }
    with pytest.raises(ValidationError):
        TargetAccountList.model_validate(payload)


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-q"]))
