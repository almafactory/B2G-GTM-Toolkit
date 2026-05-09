from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from b2g_gtm_toolkit.models.business import (
    BusinessProfile,
    CompanyStage,
    ConfidenceLevel,
    ICP,
)
from b2g_gtm_toolkit.models.gtm import (
    ActionStatus,
    GtmOutput,
    GtmOutputType,
    NotificationPreference,
    Opportunity,
    OpportunityStatus,
    Owner,
    Priority,
    Signal,
    SignalType,
    TargetAccount,
)
from b2g_gtm_toolkit.models.notion import default_workspace_manifest
from b2g_gtm_toolkit.models.secop import (
    Provenance,
    RelevanceScore,
    ResearchTaskType,
    SecopNormalizedRecord,
    SecopResearchInput,
    SourcePlatform,
)


def test_business_profile_happy_path() -> None:
    bp = BusinessProfile(
        name="Acme",
        offer_summary="ERP gubernamental",
        company_stage=CompanyStage.early,
        current_customers=["Alcaldía X"],
    )
    assert bp.name == "Acme"


def test_business_profile_requires_name() -> None:
    with pytest.raises(ValidationError):
        BusinessProfile(name="", offer_summary="x")


def test_icp_requires_some_criteria() -> None:
    with pytest.raises(ValidationError):
        ICP(name="ICP1")


def test_icp_happy_path() -> None:
    icp = ICP(
        name="Alcaldías medianas",
        target_entity_types=["alcaldia"],
        confidence_level=ConfidenceLevel.medium,
    )
    assert icp.confidence_level == ConfidenceLevel.medium


def test_target_account_fit_score_bounds() -> None:
    TargetAccount(name="Alcaldía de Cali", fit_score=80)
    with pytest.raises(ValidationError):
        TargetAccount(name="X", fit_score=120)


def test_opportunity_happy_path() -> None:
    op = Opportunity(title="Licitación 001", status=OpportunityStatus.open)
    assert op.status == OpportunityStatus.open


def test_opportunity_negative_value_fails() -> None:
    with pytest.raises(ValidationError):
        Opportunity(title="X", estimated_value=-1)


def test_owner_email_validation() -> None:
    Owner(name="Juan", email="juan@example.com", notification_preference=NotificationPreference.email)
    with pytest.raises(ValidationError):
        Owner(name="Juan", email="not-an-email")


def test_signal_happy_path() -> None:
    s = Signal(type=SignalType.new_opportunity, summary="Nueva licitación", priority=Priority.high)
    assert s.action_status == ActionStatus.pending


def test_signal_requires_summary() -> None:
    with pytest.raises(ValidationError):
        Signal(type=SignalType.new_opportunity, summary="")


def test_gtm_output_happy_path() -> None:
    out = GtmOutput(type=GtmOutputType.outreach, title="Email A", content="Hola...")
    assert out.type == GtmOutputType.outreach


def test_gtm_output_requires_title() -> None:
    with pytest.raises(ValidationError):
        GtmOutput(type=GtmOutputType.outreach, title="", content="x")


def test_secop_research_input_happy_path() -> None:
    inp = SecopResearchInput(task_type=ResearchTaskType.account_research, entity_names=["Alcaldía"])
    assert inp.result_limit == 50


def test_secop_research_input_invalid_limit() -> None:
    with pytest.raises(ValidationError):
        SecopResearchInput(task_type=ResearchTaskType.account_research, result_limit=0)


def test_secop_normalized_record_happy_path() -> None:
    rec = SecopNormalizedRecord(
        source_platform=SourcePlatform.SECOP_II,
        source_dataset="contratos_secop_ii",
        source_record_id="abc-123",
        buyer_name="Alcaldía de Cali",
        object="Servicios de TI",
        relevance=RelevanceScore(score=85, rationale="Match con ICP"),
        provenance=Provenance(
            source_dataset="contratos_secop_ii",
            retrieved_at=datetime.now(timezone.utc),
            raw_payload_hash="deadbeef",
        ),
    )
    assert rec.currency == "COP"


def test_secop_normalized_record_requires_object() -> None:
    with pytest.raises(ValidationError):
        SecopNormalizedRecord(
            source_platform=SourcePlatform.SECOP_II,
            source_dataset="ds",
            source_record_id="id",
            buyer_name="X",
            object="",
            provenance=Provenance(
                source_dataset="ds",
                retrieved_at=datetime.now(timezone.utc),
                raw_payload_hash="h",
            ),
        )


def test_default_notion_manifest_has_eight_databases() -> None:
    manifest = default_workspace_manifest()
    names = [db.name for db in manifest.databases]
    assert names == [
        "B2G Business Profiles",
        "B2G ICPs",
        "B2G Target Accounts",
        "B2G SECOP Research",
        "B2G Opportunities",
        "B2G GTM Outputs",
        "B2G Owners",
        "B2G Signals",
    ]


def test_notion_manifest_database_requires_properties() -> None:
    from b2g_gtm_toolkit.models.notion import NotionDatabaseSpec

    with pytest.raises(ValidationError):
        NotionDatabaseSpec(name="empty", properties=[])
