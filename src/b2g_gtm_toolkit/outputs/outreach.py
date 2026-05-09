from __future__ import annotations

from typing import Any, Dict, List

from ._common import _location, build_source_refs


def build_outreach_context(
    opportunity: Dict[str, Any],
    account: Dict[str, Any],
    research: List[Dict[str, Any]],
) -> Dict[str, Any]:
    account_name = account.get("name") or "la entidad"
    entity_type = account.get("entity_type") or "entidad pública"
    location = _location(account)

    source_refs = build_source_refs(research, limit=3)
    primary = source_refs[0] if source_refs else None

    opp_title = opportunity.get("title") or "una oportunidad pública reciente"

    subject_options: List[str] = [
        f"Apoyo a {account_name} en {opp_title}",
        f"Experiencia con {entity_type} similares en {location}",
    ]
    if primary and primary.get("object"):
        subject_options.append(f"Sobre {primary['object'][:60]}")

    opening_lines: List[str] = []
    if primary:
        ref_id = primary.get("process_id") or primary.get("contract_id") or primary.get("source_record_id")
        opening_lines.append(
            f"Vi el proceso {ref_id} de {account_name} ({primary.get('modality') or 'modalidad s/d'}, "
            f"{primary.get('value_formatted')}) y quería compartirle cómo apoyamos a otras entidades en {location} "
            f"con objetos similares."
        )
        if primary.get("award_date"):
            opening_lines.append(
                f"Tras el contrato adjudicado el {primary['award_date']} por {account_name}, suele aparecer "
                f"una segunda fase operativa donde podemos ayudar."
            )
    else:
        opening_lines.append(
            f"Hemos venido siguiendo el trabajo de {account_name} en {location} y queríamos compartir cómo "
            f"acompañamos a otras {entity_type}s en retos similares."
        )

    value_props: List[str] = [
        f"Implementación rápida adaptada al ciclo presupuestal de {entity_type}.",
        "Equipo con experiencia en pliegos colombianos y requisitos del RUP.",
    ]
    if primary and primary.get("object"):
        value_props.append(
            f"Casos comparables al objeto '{primary['object'][:80]}' con métricas verificables."
        )

    cta = "¿Podríamos agendar 15 minutos esta o la próxima semana para validar si tiene sentido conversar?"

    return {
        "account_name": account_name,
        "entity_type": entity_type,
        "location": location,
        "opportunity_title": opp_title,
        "subject_options": subject_options,
        "opening_lines": opening_lines,
        "value_props": value_props,
        "cta": cta,
        "source_refs": source_refs,
    }
