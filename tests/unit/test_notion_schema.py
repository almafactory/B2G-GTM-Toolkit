from __future__ import annotations

from datetime import date, datetime, timezone

from b2g_gtm_toolkit.models.gtm import ResearchStatus, TargetAccount
from b2g_gtm_toolkit.models.secop import (
    Provenance,
    SecopNormalizedRecord,
    SourcePlatform,
)
from b2g_gtm_toolkit.notion.schema import DEFAULT_MANIFEST, manifest_for
from b2g_gtm_toolkit.notion.write import (
    dedupe_filter_for_secop,
    secop_record_properties,
    target_account_properties,
)


def test_default_manifest_has_eight_databases():
    names = [db.name for db in DEFAULT_MANIFEST.databases]
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


def test_manifest_for_overrides_names():
    overrides = {"B2G ICPs": "Custom ICPs"}
    manifest = manifest_for(overrides)
    names = [db.name for db in manifest.databases]
    assert "Custom ICPs" in names
    assert "B2G ICPs" not in names


def test_target_account_properties_basic():
    account = TargetAccount(
        name="Alcaldia de Medellin",
        normalized_name="alcaldia medellin",
        entity_type="alcaldia",
        nit="800123456",
        department="Antioquia",
        municipality="Medellin",
        category="territorial",
        fit_score=82.5,
        fit_rationale="Coincide en region y categoria",
        research_status=ResearchStatus.in_progress,
        owner_ref="owner-123",
        icp_ref="icp-1",
    )
    props = target_account_properties(account)
    assert props["Name"]["title"][0]["text"]["content"] == "Alcaldia de Medellin"
    assert props["Entity Type"]["select"]["name"] == "alcaldia"
    assert props["Fit Score"]["number"] == 82.5
    assert props["Research Status"]["select"]["name"] == "in_progress"
    assert props["Owner"]["relation"][0]["id"] == "owner-123"
    assert props["ICP"]["relation"][0]["id"] == "icp-1"


def test_secop_record_properties_round_trip():
    record = SecopNormalizedRecord(
        source_platform=SourcePlatform.SECOP_II,
        source_dataset="p6dx-8zbt",
        source_record_id="abc-123",
        source_url="https://example.org/proc/abc-123",
        process_id="proc-1",
        contract_id="ctr-1",
        buyer_name="Alcaldia de Medellin",
        buyer_nit="800123456",
        supplier_name=None,
        object="Servicios de consultoria",
        modality="licitacion_publica",
        status="open",
        contract_value=1500000000.0,
        currency="COP",
        publication_date=date(2025, 1, 5),
        unspsc_codes=["80101500", "80111600"],
        matched_account_id="acc-1",
        provenance=Provenance(
            source_dataset="p6dx-8zbt",
            retrieved_at=datetime.now(timezone.utc),
            raw_payload_hash="hash-1",
        ),
        run_id="run-2025-01-05",
    )
    props = secop_record_properties(record)
    assert props["Object"]["title"][0]["text"]["content"] == "Servicios de consultoria"
    assert props["Source Platform"]["select"]["name"] == "SECOP_II"
    assert props["Contract Value"]["number"] == 1500000000.0
    assert props["UNSPSC Codes"]["multi_select"] == [
        {"name": "80101500"},
        {"name": "80111600"},
    ]
    assert props["Target Account"]["relation"][0]["id"] == "acc-1"
    assert props["Run ID"]["rich_text"][0]["text"]["content"] == "run-2025-01-05"
    assert props["Raw Payload Hash"]["rich_text"][0]["text"]["content"] == "hash-1"

    dedupe = dedupe_filter_for_secop(record)
    assert dedupe["and"][0]["select"]["equals"] == "SECOP_II"
    assert dedupe["and"][1]["rich_text"]["equals"] == "abc-123"
