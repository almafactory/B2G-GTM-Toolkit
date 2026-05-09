# ICP Brief — B2G Colombia

> Salida del flujo de definición de ICP. Cada sección corresponde a un campo del modelo `ICP`. Mantener el lenguaje del sector público colombiano (entidad, ordenador del gasto, supervisor, plan de adquisiciones, SECOP).

## Identidad del ICP

- **Nombre del ICP** (`name`):
  *(corto, reutilizable en conversación, ej. "Alcaldías categoría 1–2 con secretaría TIC")*
- **Referencia al business profile** (`business_profile_ref`):

## Segmento objetivo

- **Tipos de entidad pública** (`target_entity_types`):
  *(alcaldía, gobernación, ministerio, ESE, IE oficial, EICE, etc.)*
  -
- **Categorías / subgrupos** (`target_categories`):
  *(ej. "categoría 1", "ESE de mediana complejidad", "minTIC y entidades adscritas")*
  -
- **Regiones objetivo** (`target_regions`):
  -

## Criterios de fit (`fit_criteria`)

Atributos que aparecen en ≥80% de los Tier A.

-
-
-

## Descalificadores (`disqualifiers`)

Patrones que predicen pérdida o costo desproporcionado.

-
-

## Triggers de compra (`buying_triggers`)

Eventos del sector público colombiano que crean urgencia.

- Primario:
- Secundario(s):

## Comité de compra (`buying_committee_roles`)

Por cada rol indica títulos típicos e influencia.

- **Ordenador del gasto**
  - Títulos típicos: alcalde, gobernador, director general, gerente
  - Influencia: aprobador final
- **Sponsor funcional**
  - Títulos típicos: secretario(a) de TIC / Salud / Educación / Hacienda / Planeación
  - Influencia:
- **Campeón / líder técnico**
  - Títulos típicos: jefe de oficina, profesional especializado
  - Influencia:
- **Jurídico y contratación**
  - Títulos típicos: jefe oficina jurídica, asesor de contratación
  - Influencia: bloqueador procesal
- **Supervisor del contrato**
  - Títulos típicos:
  - Influencia:

## Señales observables (`observable_signals`)

Cómo se detecta desde afuera que el ICP calza y el trigger se disparó.

- Procesos en SECOP relacionados con:
- Plan Anual de Adquisiciones con rubros:
- Notas de prensa o actos administrativos sobre:
- Cambios directivos:
- Indicadores presupuestales:

## Resumen de evidencia (`evidence_summary`)

> Cómo se construyó este ICP: cuántos Tier A, qué patrones se repitieron, qué se asumió.

## Nivel de confianza (`confidence_level`)

- [ ] low — < 5 Tier A. Hipótesis, validar agresivamente.
- [ ] medium — 5–15 Tier A. Direccionalmente correcto.
- [ ] high — 15+ Tier A. Patrón validado.

## Estado de aprobación (`approval_status`)

- [x] draft
- [ ] needs_review
- [ ] approved
- [ ] rejected
- [ ] archived
