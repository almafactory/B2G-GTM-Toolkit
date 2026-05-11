from __future__ import annotations

import json
from pathlib import Path

from b2g_gtm_toolkit.models.secop import ResearchTaskType, SecopResearchInput, SourcePlatform
from b2g_gtm_toolkit.secop.datasets import DATASETS, get_dataset
from b2g_gtm_toolkit.secop.dedupe import dedupe
from b2g_gtm_toolkit.secop.normalize import normalize_record, parse_currency, parse_date
from b2g_gtm_toolkit.secop.research import _input_filters_to_where, default_offline_fixtures, run_research


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "secop"


def _load(name: str) -> list[dict]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_parse_currency_handles_strings_and_numbers():
    assert parse_currency("1.250.000.000") == 1250000000.0
    assert parse_currency("350000000") == 350000000.0
    assert parse_currency(95000000) == 95000000.0
    assert parse_currency(None) is None
    assert parse_currency("") is None


def test_parse_date_iso_and_short():
    assert parse_date("2025-08-01T00:00:00.000").isoformat() == "2025-08-01"
    assert parse_date("2025-09-12").isoformat() == "2025-09-12"
    assert parse_date(None) is None


def test_normalize_record_procesos():
    dataset = get_dataset("secop_ii_procesos")
    raw = _load("secop_ii_procesos.sample.json")[0]
    rec = normalize_record(raw, dataset, query={"task": "test"})
    assert rec.source_platform == SourcePlatform.SECOP_II
    assert rec.source_dataset == dataset.dataset_id
    assert rec.process_id == "CO1.PCCNTR.0001"
    assert rec.buyer_name == "ALCALDIA DE MEDELLIN"
    assert rec.buyer_nit == "890905211"
    assert rec.contract_value == 350000000.0
    assert rec.publication_date.isoformat() == "2025-08-01"
    assert "43232300" in rec.unspsc_codes
    assert rec.provenance.raw_payload_hash
    assert rec.provenance.query == {"task": "test"}


def test_normalize_record_contratos():
    dataset = get_dataset("secop_ii_contratos")
    raw = _load("secop_ii_contratos.sample.json")[0]
    rec = normalize_record(raw, dataset)
    assert rec.contract_id == "CO1.CTR.0001"
    assert rec.process_id == "CO1.PCCNTR.0001"
    assert rec.supplier_name == "TECH SOLUCIONES SAS"
    assert rec.contract_value == 320000000.0
    assert rec.start_date.isoformat() == "2025-10-01"
    assert rec.end_date.isoformat() == "2026-09-30"


def test_dedupe_keeps_one_per_logical_key():
    dataset = get_dataset("secop_ii_procesos")
    raws = _load("secop_ii_procesos.sample.json")
    records = [normalize_record(r, dataset) for r in raws]
    deduped = dedupe(records)
    process_ids = sorted([r.process_id for r in deduped])
    assert process_ids == ["CO1.PCCNTR.0001", "CO1.PCCNTR.0002", "CO1.PCCNTR.0003"]


def test_run_research_offline_writes_jsonl(tmp_path: Path):
    input_data = SecopResearchInput(
        task_type=ResearchTaskType.opportunity_discovery,
        entity_nits=["890905211"],
        datasets=["secop_ii_procesos", "secop_ii_contratos"],
        result_limit=50,
        page_size=50,
    )
    fixtures = default_offline_fixtures(FIXTURE_DIR)
    run = run_research(input_data, output_root=tmp_path, offline_fixtures=fixtures)
    assert run.jsonl_path.exists()
    assert run.manifest_path.exists()
    lines = [json.loads(l) for l in run.jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == run.deduped_count
    assert run.deduped_count >= 3
    for line in lines:
        assert "provenance" in line
        assert "raw_payload_hash" in line["provenance"]
        assert "retrieved_at" in line["provenance"]
    manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
    assert manifest["raw_count"] >= run.deduped_count
    assert manifest["deduped_count"] == run.deduped_count


def test_input_filters_include_entity_name_municipality_and_keywords():
    dataset = get_dataset("secop_ii_procesos")
    input_data = SecopResearchInput(
        task_type=ResearchTaskType.opportunity_discovery,
        entity_names=["Alcaldia de Soledad"],
        municipalities=["Soledad"],
        keywords=["ERP", "software financiero"],
    )

    where = _input_filters_to_where(input_data, dataset)

    assert where is not None
    assert "entidad like '%ALCALDIA DE SOLEDAD%'" in where
    assert "ciudad_entidad like '%Soledad%'" in where
    assert "ciudad_entidad like '%SOLEDAD%'" in where
    assert "descripci_n_del_procedimiento like '%ERP%'" in where
    assert "descripci_n_del_procedimiento like '%SOFTWARE FINANCIERO%'" in where


def test_dataset_registry_has_expected_datasets():
    for name in ("secop_ii_procesos", "secop_ii_contratos", "secop_i_procesos"):
        assert name in DATASETS
        ds = DATASETS[name]
        assert ds.dataset_id
        assert ds.base_url.startswith("https://www.datos.gov.co")
        assert ds.field_map
