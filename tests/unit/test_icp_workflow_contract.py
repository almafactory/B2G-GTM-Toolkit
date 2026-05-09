from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from b2g_gtm_toolkit.models.business import (
    ApprovalStatus,
    BusinessProfile,
    BuyingCommitteeRole,
    CompanyStage,
    ConfidenceLevel,
    ICP,
)

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "business-profile.sample.json"


def test_sample_business_profile_validates() -> None:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    profile = BusinessProfile.model_validate(raw)

    assert profile.name == "GobCloud SAS"
    assert profile.company_stage == CompanyStage.growth
    assert "Alcaldia de Manizales" in profile.current_customers
    assert profile.best_customers, "Tier A debe estar poblado"
    assert profile.poor_fit_customers, "Tier C debe estar poblado"
    assert "Caldas" in profile.regions_served


def test_business_profile_requires_name_and_offer() -> None:
    with pytest.raises(ValidationError):
        BusinessProfile.model_validate({"name": "", "offer_summary": "algo"})

    with pytest.raises(ValidationError):
        BusinessProfile.model_validate({"name": "X", "offer_summary": ""})


def test_sample_icp_payload_validates() -> None:
    payload = {
        "name": "Alcaldias categoria 1-2 con secretaria TIC",
        "business_profile_ref": "GobCloud SAS",
        "target_entity_types": ["alcaldia", "gobernacion"],
        "target_categories": ["categoria 1", "categoria 2", "categoria especial"],
        "target_regions": ["Eje Cafetero", "Cundinamarca", "Boyaca"],
        "fit_criteria": [
            "Categoria municipal 1, 2 o especial",
            "Secretaria TIC formalizada en estructura",
            "Plan Anual de Adquisiciones publicado en SECOP II",
            "Presupuesto de inversion > 30.000 SMMLV",
        ],
        "disqualifiers": [
            "Municipios categoria 6 sin transferencias suficientes",
            "Pliegos atados a competidor incumbente",
        ],
        "buying_triggers": [
            "Aprobacion de nuevo plan de desarrollo cuatrienal",
            "Hallazgos de Contraloria en gestion documental",
            "Vencimiento de contrato del incumbente",
        ],
        "buying_committee_roles": [
            {
                "role": "Ordenador del gasto",
                "typical_titles": ["Alcalde", "Gobernador"],
                "influence": "aprobador final",
            },
            {
                "role": "Sponsor funcional",
                "typical_titles": ["Secretario TIC", "Secretario General"],
                "influence": "patrocina y prioriza",
            },
            {
                "role": "Jefe de contratacion",
                "typical_titles": ["Jefe Oficina Juridica"],
                "influence": "bloqueador procesal",
            },
        ],
        "observable_signals": [
            "Procesos publicados en SECOP II en categoria gestion documental",
            "PAA con rubros TIC vigentes",
            "Cambio reciente de secretario(a) TIC",
        ],
        "confidence_level": "medium",
        "evidence_summary": "6 clientes Tier A en Eje Cafetero, patron repetido en categoria 1-2.",
        "approval_status": "needs_review",
    }

    icp = ICP.model_validate(payload)

    assert icp.confidence_level == ConfidenceLevel.medium
    assert icp.approval_status == ApprovalStatus.needs_review
    assert len(icp.buying_committee_roles) == 3
    assert all(isinstance(r, BuyingCommitteeRole) for r in icp.buying_committee_roles)
    assert "alcaldia" in icp.target_entity_types


def test_icp_requires_target_or_fit_criteria() -> None:
    with pytest.raises(ValidationError):
        ICP.model_validate(
            {
                "name": "ICP vacio",
                "target_entity_types": [],
                "fit_criteria": [],
            }
        )


def test_icp_with_only_target_entity_types_is_valid() -> None:
    icp = ICP.model_validate(
        {
            "name": "Solo segmento",
            "target_entity_types": ["alcaldia"],
        }
    )
    assert icp.fit_criteria == []
