---
name: b2g-output-workflows
description: Generar entregables accionables para Account Executives B2G a partir de oportunidades investigadas en SECOP — outreach (cold email / LinkedIn first-touch), preparación previa a discovery meeting, calificación MEDDPICC ligero adaptado al sector público colombiano, y propuesta / business case con justificación basada en evidencia SECOP.
triggers:
  - generar outreach B2G
  - cold email gobierno Colombia
  - first-touch LinkedIn alcaldía
  - preparar reunión discovery sector público
  - briefing previo a reunión gubernamental
  - calificar oportunidad B2G
  - MEDDPICC sector público
  - propuesta gubernamental
  - business case B2G
  - justificación con referencias SECOP
---

# Flujo de generación de entregables AE para ventas B2G

Esta skill toma una **oportunidad investigada** (cuenta objetivo + oportunidad SECOP + registros normalizados con provenance) y produce entregables listos para que un Account Executive ejecute la próxima acción de venta. Toda salida debe poder validarse contra el modelo `GtmOutput` del paquete `b2g_gtm_toolkit.models.gtm`, y debe citar al menos una referencia a un proceso o contrato SECOP cuando exista evidencia.

## Cuándo usar esta skill

Activa esta skill cuando el usuario pida:
- Redactar un **outreach** (correo en frío o primer mensaje en LinkedIn) para una entidad pública específica.
- Preparar un **briefing previo a una reunión** (discovery o follow-up) con un comprador del sector público.
- Calificar la oportunidad con un **MEDDPICC ligero** adaptado a B2G.
- Construir una **propuesta corta** o **business case** con evidencia SECOP (procesos previos, contratos adjudicados, valores históricos, modalidades).

## Entregables

| Tipo | Builder | Plantilla |
| --- | --- | --- |
| `outreach` | `outputs.outreach.build_outreach_context` | `templates/outreach.md` |
| `meeting-prep` | `outputs.meeting_prep.build_meeting_prep_context` | `templates/meeting-prep.md` |
| `proposal` | `outputs.proposal_brief.build_proposal_context` | `templates/proposal-brief.md` |

Cada builder retorna un diccionario determinístico (sin LLM) con campos normalizados y una lista `source_refs` con referencias SECOP. En un flujo real, el agente debe leer la oportunidad o cuenta objetivo desde Notion y guardar el entregable en `B2G GTM Outputs` con `b2g-gtm output create --type <tipo> --opportunity-page <page-id> --to-notion --apply` o `--target-account-page <page-id> --to-notion --apply`. `--source <archivo.json>` queda para previews locales, pruebas o importaciones explícitas.

## Permisos y datos externos

Si el entregable necesita un archivo, una oportunidad de Notion, acceso a un documento comercial o confirmación del AE, pide **una sola acción del usuario a la vez**. Ejemplos: "comparte la oportunidad investigada", luego "confirma el rol del comprador", luego "autoriza guardar el entregable en Notion". No conviertas el bloqueo en una lista de comandos o requisitos técnicos.

## Metodología

Adaptada de las skills internas de ventas (`E:\skills\ventas\gtm-outreach-strategy.md`, `gtm-meeting-prep.md`, `gtm-qualification-scoring.md`) al contexto B2G colombiano.

### 1. Outreach (cold email / LinkedIn first-touch)

Objetivo: lograr una primera reunión de descubrimiento con el rol relevante (Secretario, Director de TI, Jefe de Contratación, Gerente).

Estructura del builder:
- `subject_options`: 2–3 asuntos cortos, específicos a la entidad y a un proceso SECOP reciente.
- `opening_lines`: aperturas que muestran homework — referencian el municipio/departamento, una modalidad recurrente o un contrato reciente.
- `value_props`: 2–3 propuestas de valor alineadas al objeto contractual histórico de la entidad.
- `cta`: pedido concreto de 15–20 minutos.
- `source_refs`: lista de procesos/contratos SECOP citados, cada uno con `source_record_id`, `object`, `value`, `url`.

Reglas:
- Cero plantillas genéricas: cada apertura debe poder rastrearse a un campo del registro SECOP citado.
- Si no hay registros SECOP, marcar `source_refs` vacío y advertir en el output que la personalización será limitada.
- Usar lenguaje formal-pero-cercano. No usar jerga corporativa anglosajona.

### 2. Preparación de reunión (briefing previo a discovery)

Objetivo: que el AE llegue a la reunión con contexto del comprador, historial reciente y agenda propuesta.

Estructura del builder:
- `attendees`: comprador (entidad + rol estimado) y vendedor.
- `recent_secop_history`: top 3–5 procesos/contratos recientes de la entidad, ordenados por fecha.
- `key_objections`: objeciones B2G típicas (presupuesto plurianual, vigencias futuras, requisitos de pliego, experiencia mínima exigida).
- `talking_points`: preguntas abiertas para discovery (problema, criterios de decisión, proceso, dolor, campeón).
- `source_refs`: ídem outreach.

Reglas:
- El historial SECOP siempre debe citar al menos `process_id` o `contract_id` y la fecha.
- Los talking points deben mapear a la metodología MEDDPICC (Metric, Economic Buyer, Decision Criteria, Decision Process, Pain, Champion) adaptada — sin pedir Competition explícita en B2G porque el "competidor" es el pliego.

### 3. Calificación MEDDPICC ligero (B2G)

Embebida dentro del briefing de reunión y la propuesta. Las dimensiones se traducen así:
- **M (Metric)**: ahorro proyectado vs. valor histórico promedio adjudicado por la entidad para objetos similares.
- **E (Economic Buyer)**: ordenador del gasto / Secretario / Director (no el comité técnico).
- **D (Decision Criteria)**: criterios de pliego, experiencia mínima, requisitos jurídicos.
- **P (Decision Process)**: modalidad esperada (licitación pública, selección abreviada, mínima cuantía, contratación directa, acuerdo marco).
- **P (Pain)**: dolor operativo evidenciado por contratos previos (recurrencia, valor creciente, fallos declarados desiertos).
- **I (Identified)**: campeón identificado dentro de la entidad.
- **C (Champion)**: rol con poder de empuje interno.
- **C (Compliance)**: requisitos de transparencia, conflicto de interés, RUP.

### 4. Propuesta / business case

Objetivo: justificación corta (1–2 páginas) que el AE pueda enviar como follow-up.

Estructura del builder:
- `problem_statement`: descripción del problema en términos del objeto contractual histórico.
- `evidence_block`: 3–5 referencias SECOP con `process_id`, `object`, `value`, `award_date`, `modality`. Esta es la sección no-negociable: sin evidencia, no hay propuesta.
- `proposed_value`: oferta concreta alineada al objeto.
- `business_case_summary`: 3–4 líneas con métrica esperada (M de MEDDPICC), modalidad sugerida y siguiente paso.
- `source_refs`: ídem.

Reglas:
- Cada bullet del `evidence_block` debe enlazar a `source_url` cuando esté disponible.
- Si la oportunidad ya tiene `estimated_value`, usarlo como ancla; si no, calcular media de los registros SECOP citados.

## Flujo recomendado

1. El AE selecciona una oportunidad o cuenta objetivo en Notion.
2. El agente genera internamente el tipo de entregable necesario (`outreach`, `meeting-prep` o `proposal`) leyendo el contexto canónico desde Notion.
3. Con autorización explícita, el agente escribe o actualiza el entregable en `B2G GTM Outputs`.
4. El agente reporta si la página de Notion fue creada o actualizada, el registro de negocio al que quedó asociada y el siguiente paso comercial.
5. El AE revisa tono y supuestos en Notion antes de enviar o aprobar. Los archivos locales sólo se usan para vista previa, importación o diagnóstico.

## Validación

- El builder debe ser una función pura, sin llamadas a LLM ni a red.
- El markdown ensamblado debe contener al menos una referencia a un `source_record_id` cuando `research` no esté vacío.
- Snapshot tests en `tests/unit/test_outputs.py` verifican estabilidad de la salida.
