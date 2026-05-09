from __future__ import annotations

from typing import Any, Dict, List

from ._common import _format_cop, _location, average_value, build_source_refs


def build_proposal_context(
    opportunity: Dict[str, Any],
    account: Dict[str, Any],
    research: List[Dict[str, Any]],
) -> Dict[str, Any]:
    account_name = account.get("name") or "la entidad"
    entity_type = account.get("entity_type") or "entidad pública"
    location = _location(account)

    source_refs = build_source_refs(research, limit=5)

    primary_object = None
    if source_refs and source_refs[0].get("object"):
        primary_object = source_refs[0]["object"]

    if primary_object:
        problem_statement = (
            f"{account_name} ({entity_type}, {location}) ha contratado de forma recurrente objetos asociados a "
            f"'{primary_object}'. La operación muestra una necesidad sostenida que conviene atender con un "
            f"enfoque consolidado en lugar de procesos puntuales."
        )
    else:
        problem_statement = (
            f"{account_name} ({entity_type}, {location}) enfrenta un reto operativo recurrente que justifica "
            f"una solución consolidada."
        )

    evidence_block: List[Dict[str, Any]] = []
    for ref in source_refs:
        evidence_block.append(
            {
                "ref_id": ref.get("process_id") or ref.get("contract_id") or ref.get("source_record_id"),
                "object": ref.get("object"),
                "modality": ref.get("modality"),
                "value_formatted": ref.get("value_formatted"),
                "date": ref.get("award_date") or ref.get("publication_date"),
                "url": ref.get("url"),
            }
        )

    anchor_value = opportunity.get("estimated_value") or average_value(research)
    anchor_value_formatted = _format_cop(anchor_value) if anchor_value is not None else "s/d"

    proposed_value = (
        f"Acompañamiento integral con entrega medible alineada al objeto recurrente "
        f"y al ciclo presupuestal de {entity_type}. Valor ancla estimado: {anchor_value_formatted}."
    )

    modality = opportunity.get("modality") or (source_refs[0].get("modality") if source_refs else None) or "modalidad por definir"
    next_action = opportunity.get("next_action") or "Confirmar disponibilidad presupuestal y agendar mesa técnica."

    business_case_summary_lines: List[str] = [
        f"Métrica esperada: reducción de costo unitario y/o tiempo de proceso vs. valor ancla ({anchor_value_formatted}).",
        f"Modalidad sugerida: {modality}.",
        f"Evidencia citada: {len(evidence_block)} registro(s) SECOP.",
        f"Siguiente paso: {next_action}",
    ]

    return {
        "account_name": account_name,
        "entity_type": entity_type,
        "location": location,
        "opportunity_title": opportunity.get("title") or "(sin título)",
        "problem_statement": problem_statement,
        "evidence_block": evidence_block,
        "proposed_value": proposed_value,
        "anchor_value_formatted": anchor_value_formatted,
        "business_case_summary": business_case_summary_lines,
        "source_refs": source_refs,
    }
