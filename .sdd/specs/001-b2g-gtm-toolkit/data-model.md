# Modelo de datos: B2G-GTM-Toolkit

**ID de la funcionalidad**: `001-b2g-gtm-toolkit`
**Creado**: 2026-05-09
**Estado**: Draft

## Panorama general

El modelo de datos se centra en Notion como workspace GTM durable y en logs locales JSONL de ejecución como capa de staging auditable. El modelo mantiene la evidencia de contratación separada de la interpretación GTM para que los agentes puedan generar briefs útiles sin perder la trazabilidad de la fuente.

## Entidades

### Business Profile

Representa la empresa contratista o B2G que usa el toolkit.

**Campos**:
- `name`
- `offer_summary`
- `products_services`
- `current_customers`
- `best_customers`
- `poor_fit_customers`
- `competitors`
- `company_stage`
- `regions_served`
- `constraints`
- `created_at`
- `updated_at`

**Relaciones**:
- Tiene muchos registros `ICP`.

### ICP

Representa el perfil ideal de cliente del sector público.

**Campos**:
- `name`
- `target_entity_types`
- `target_categories`
- `target_regions`
- `fit_criteria`
- `disqualifiers`
- `buying_triggers`
- `buying_committee_roles`
- `observable_signals`
- `confidence_level`
- `evidence_summary`
- `approval_status`

**Relaciones**:
- Pertenece a un `Business Profile`.
- Tiene muchos registros `Target Account`.

### Target Account

Representa una entidad pública o segmento de cuenta que vale la pena investigar.

**Campos**:
- `name`
- `normalized_name`
- `entity_type`
- `nit`
- `department`
- `municipality`
- `category`
- `fit_score`
- `fit_rationale`
- `research_status`
- `owner`
- `last_researched_at`

**Relaciones**:
- Pertenece a un `ICP`.
- Tiene muchos registros `SECOP Research Record`.
- Tiene muchos registros `Opportunity`.
- Tiene un `Owner` responsable.

### SECOP Research Record

Representa un hallazgo de contratación de fuente oficial antes de la interpretación GTM.

**Campos**:
- `source_platform`
- `source_dataset`
- `source_record_id`
- `source_url`
- `process_id`
- `contract_id`
- `buyer_name`
- `buyer_nit`
- `supplier_name`
- `supplier_nit`
- `object`
- `modality`
- `status`
- `contract_value`
- `currency`
- `publication_date`
- `award_date`
- `start_date`
- `end_date`
- `deadline`
- `unspsc_codes`
- `raw_payload_hash`
- `run_id`
- `provenance_notes`

**Relaciones**:
- Pertenece a un `Target Account` cuando hace match.
- Puede crear o soportar una `Opportunity`.

### Opportunity

Representa una licitación, proceso de compra u oportunidad comercial accionable.

**Campos**:
- `title`
- `summary`
- `status`
- `source_platform`
- `source_url`
- `estimated_value`
- `deadline`
- `modality`
- `requirements_summary`
- `fit_score`
- `fit_rationale`
- `pursuit_recommendation`
- `next_action`
- `approval_status`

**Relaciones**:
- Pertenece a un `Target Account`.
- Hace referencia a uno o más registros `SECOP Research Record`.
- Tiene muchos registros `GTM Output`.
- Puede tener muchos registros `Signal` en la iteración 2.

### GTM Output

Representa entregables comerciales generados.

**Campos**:
- `type` (`outreach`, `meeting_prep`, `proposal_brief`, `business_case`)
- `title`
- `content`
- `source_summary`
- `approval_status`
- `created_for`
- `created_at`
- `updated_at`

**Relaciones**:
- Pertenece a un `Target Account` o `Opportunity`.
- Hace referencia a registros de soporte `SECOP Research Record`.

### Owner

Representa a la persona responsable de cuentas, oportunidades o señales futuras.

**Campos**:
- `name`
- `role`
- `email`
- `slack_id`
- `notification_preference`
- `active`

**Relaciones**:
- Es responsable de registros `Target Account`, `Opportunity` y futuros `Signal`.

### Signal

Planeado para la iteración 2, pero incluido temprano en el esquema.

**Campos**:
- `type`
- `priority`
- `summary`
- `source`
- `source_url`
- `detected_at`
- `recommended_action`
- `notification_status`
- `action_status`

**Relaciones**:
- Pertenece a un `Target Account` o `Opportunity`.
- Se asigna a un `Owner`.

## Mapeo de bases de datos de Notion

| Base de datos de Notion | Entidad |
|-----------------|--------|
| `B2G Business Profiles` | Business Profile |
| `B2G ICPs` | ICP |
| `B2G Target Accounts` | Target Account |
| `B2G SECOP Research` | SECOP Research Record |
| `B2G Opportunities` | Opportunity |
| `B2G GTM Outputs` | GTM Output |
| `B2G Owners` | Owner |
| `B2G Signals` | Signal |

## Estrategia de dedupe

Los registros de investigación deben usar una clave externa estable cuando esté disponible. Cuando no haya una sola clave confiable, usar una clave compuesta:

```text
source_platform + source_dataset + process_id/contract_id + buyer_nit + supplier_nit + normalized_object + date + value
```

Los target accounts deben usar `nit` cuando esté disponible. Si no, usar nombre normalizado más municipio/departamento.

Las oportunidades deben deduplicarse por URL de origen, ID de proceso o título normalizado más comprador más fecha límite.

## Estados de aprobación

Los registros que impulsan trabajo aguas abajo deben soportar:
- `draft`
- `needs_review`
- `approved`
- `rejected`
- `archived`

Esto evita que el agente use ICPs inciertos, oportunidades o salidas generadas sin revisión del usuario.
