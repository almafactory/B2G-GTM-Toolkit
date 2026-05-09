from __future__ import annotations

from typing import Any, Dict, List

from ._common import _location, build_source_refs


def build_meeting_prep_context(
    opportunity: Dict[str, Any],
    account: Dict[str, Any],
    research: List[Dict[str, Any]],
) -> Dict[str, Any]:
    account_name = account.get("name") or "la entidad"
    entity_type = account.get("entity_type") or "entidad pública"
    location = _location(account)

    source_refs = build_source_refs(research, limit=5)

    attendees = {
        "buyer": {
            "entity": account_name,
            "entity_type": entity_type,
            "location": location,
            "expected_role": account.get("primary_contact_role")
                or "Ordenador del gasto / Director de área / Jefe de Contratación",
        },
        "seller": {
            "role": "Account Executive B2G",
            "objective": "Discovery de problema y criterios de decisión",
        },
    }

    recent_secop_history: List[Dict[str, Any]] = []
    for ref in source_refs:
        recent_secop_history.append(
            {
                "ref_id": ref.get("process_id") or ref.get("contract_id") or ref.get("source_record_id"),
                "object": ref.get("object"),
                "modality": ref.get("modality"),
                "value_formatted": ref.get("value_formatted"),
                "date": ref.get("award_date") or ref.get("publication_date"),
                "url": ref.get("url"),
            }
        )

    key_objections: List[str] = [
        "Disponibilidad presupuestal y vigencias futuras.",
        "Cumplimiento de experiencia mínima exigida en pliegos previos.",
        "Riesgo jurídico y requisitos del RUP.",
        "Tiempos del proceso vs. necesidad operativa.",
    ]

    talking_points: List[str] = [
        f"Metric: ¿qué resultado mediría el éxito frente al promedio histórico de {account_name}?",
        "Economic Buyer: ¿quién firma como ordenador del gasto?",
        "Decision Criteria: ¿qué criterios de pliego son innegociables (experiencia, certificaciones, capacidad financiera)?",
        "Decision Process: ¿qué modalidad esperan usar (licitación, selección abreviada, mínima cuantía, contratación directa)?",
        "Pain: ¿qué dolor operativo motivó los procesos recientes?",
        "Champion: ¿quién dentro del equipo técnico podría empujar internamente?",
        "Compliance: ¿hay restricciones de transparencia o conflicto de interés a anticipar?",
    ]

    return {
        "account_name": account_name,
        "entity_type": entity_type,
        "location": location,
        "opportunity_title": opportunity.get("title") or "(sin título)",
        "opportunity_status": opportunity.get("status"),
        "opportunity_modality": opportunity.get("modality"),
        "attendees": attendees,
        "recent_secop_history": recent_secop_history,
        "key_objections": key_objections,
        "talking_points": talking_points,
        "source_refs": source_refs,
    }
