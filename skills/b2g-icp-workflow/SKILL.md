---
name: b2g-icp-workflow
description: Construir o presionar el Ideal Customer Profile (ICP) de una empresa B2B que vende al sector público colombiano (alcaldías, gobernaciones, ministerios, entes descentralizados, empresas estatales) a partir de su contexto real de clientes.
triggers:
  - definir ICP B2G
  - construir ICP gubernamental
  - perfil de cliente ideal sector público
  - ICP alcaldías
  - ICP gobernaciones
  - pressure-test ICP B2G
  - validar ICP gobierno Colombia
---

# Flujo de definición de ICP B2G (sector público colombiano)

Esta skill guía al agente para producir un **ICP B2G** accionable a partir del contexto real de la empresa. El resultado debe poder validarse contra los modelos `BusinessProfile` e `ICP` del paquete `b2g_gtm_toolkit.models.business`.

## Cuándo usar esta skill

Actívala cuando el usuario pida:
- Definir un ICP nuevo para vender al Estado colombiano.
- Presionar/refinar un ICP existente con datos reales de clientes.
- Traducir su negocio a segmentos del sector público (alcaldías, gobernaciones, ministerios, entes descentralizados, empresas estatales, organismos de control).

## Entregables

1. Un **Business Profile** completo (siguiendo `templates/business-profile.md`) que se pueda serializar a JSON conforme al modelo `BusinessProfile`.
2. Un **ICP Brief** (siguiendo `templates/icp-brief.md`) que se pueda serializar a JSON conforme al modelo `ICP`.

## Metodología (resumen)

Basada en `gtm-icp-definition` (E:\skills\ventas\gtm-icp-definition.md), adaptada al contexto B2G colombiano.

### Paso 1 — Recolectar contexto del negocio
Pide al usuario, **una pregunta a la vez**, y registra en la plantilla `business-profile.md`:
- Nombre de la empresa y resumen de oferta (`name`, `offer_summary`).
- Productos/servicios concretos (`products_services`).
- Lista de clientes actuales (`current_customers`). Si tiene menos de 5, marca confianza baja.
- Mejores clientes (Tier A — `best_customers`): quiénes adoptan rápido, expanden, son fáciles de servir.
- Clientes mal calce (Tier C — `poor_fit_customers`): quiénes churnaron, fueron costosos o nunca adoptaron.
- Competidores reconocibles en licitaciones o en la conversación (`competitors`).
- Etapa de la empresa (`company_stage`: idea/early/growth/scale/enterprise).
- Regiones servidas en Colombia (`regions_served`: ej. "Bogotá D.C.", "Antioquia", "Cundinamarca").
- Restricciones reales (`constraints`: capacidad financiera para pólizas, RUP, equipo jurídico, idioma, etc.).

> Si el usuario no sabe alguna respuesta, déjala vacía y márcala como gap a validar; no inventes.

### Paso 2 — Identificar segmentos B2G candidatos
Mapea la oferta a tipos de entidad pública. Categorías típicas en Colombia:
- **Territoriales:** alcaldías municipales (categorías 1 a 6 y especial), gobernaciones, asambleas, concejos.
- **Nivel nacional:** ministerios, departamentos administrativos, superintendencias, agencias.
- **Descentralizados:** establecimientos públicos, unidades administrativas especiales, institutos.
- **Empresas estatales:** EICEs, sociedades de economía mixta, empresas de servicios públicos oficiales.
- **Organismos autónomos / control:** Contraloría, Procuraduría, Defensoría, Registraduría, entes universitarios autónomos.
- **Salud y educación:** ESE (hospitales públicos), IPS públicas, IE oficiales, SED/SES.

Para cada segmento candidato evalúa: tamaño de presupuesto típico, frecuencia de procesos en SECOP, modalidades de contratación predominantes (mínima cuantía, selección abreviada, licitación pública, contratación directa, acuerdos marco).

### Paso 3 — Derivar criterios de fit (`fit_criteria`)
A partir de los Tier A, extrae 3 a 5 atributos que aparezcan en ≥80% de ellos. Ejemplos B2G:
- Categoría de municipio (1, 2 o especial).
- Presupuesto anual de inversión > X COP.
- Tiene secretaría/oficina TIC formalizada.
- Ha publicado procesos en SECOP II en los últimos 12 meses.
- Cuenta con plan de desarrollo vigente que menciona la línea de la oferta.

### Paso 4 — Definir descalificadores (`disqualifiers`)
Lo que jamás cierra o cuesta demasiado:
- Municipios categoría 6 sin transferencias suficientes.
- Entidades sin RUP exigible al proveedor del tamaño del usuario.
- Procesos con pliegos atados a un competidor incumbente.
- Falta de plan de adquisiciones publicado.

### Paso 5 — Triggers de compra (`buying_triggers`)
Eventos que crean urgencia en el sector público colombiano:
- Cambio de gobierno (cada 4 años territorial / nacional).
- Aprobación de plan de desarrollo o plan de adquisiciones nuevo.
- Llegada de recursos de regalías, SGP o cooperación.
- Hallazgos de Contraloría que obligan a remediar.
- Vencimiento de contrato del incumbente.
- Emergencia o declaratoria de calamidad.
- Reforma normativa que obliga a adopción (ej. nueva resolución MinTIC, MinSalud, MinEducación).

### Paso 6 — Comité de compra (`buying_committee_roles`)
Roles típicos en una entidad pública colombiana:
- **Ordenador del gasto** (alcalde, gobernador, director, gerente) — economic buyer.
- **Secretario(a) de despacho del área funcional** (Hacienda, TIC, Salud, Educación, Planeación) — sponsor.
- **Jefe de la oficina técnica/operativa** — campeón y end-user funcional.
- **Jefe de contratación / oficina jurídica** — influenciador procesal, posible bloqueador.
- **Supervisor del contrato** — end-user que firma actas.
- **Control interno / Contraloría** — bloqueador asimétrico.

### Paso 7 — Señales observables (`observable_signals`)
Lo que el agente puede ver desde afuera para detectar fit + trigger:
- Procesos relacionados publicados en SECOP I/II/TVEC.
- Plan Anual de Adquisiciones con rubros afines.
- Notas de prensa sobre el plan de desarrollo o convenios.
- Cambios de directivos publicados en Diario Oficial / actas.
- Avance presupuestal en portales de transparencia.

### Paso 8 — Confianza (`confidence_level`)
- `low`: < 5 clientes Tier A en sector público. ICP es hipótesis.
- `medium`: 5–15 clientes Tier A. Direccionalmente correcto.
- `high`: 15+ Tier A. Patrón validado.

## Cómo opera el agente

1. Lee `templates/business-profile.md` y úsalo como guion para entrevistar al usuario.
2. Llena la plantilla campo por campo. Si falta información crítica, **pregunta**, no inventes.
3. Cuando tengas el business profile, propón 1 a 3 segmentos B2G candidatos y deja que el usuario priorice.
4. Para el segmento priorizado, completa `templates/icp-brief.md`.
5. Genera también una versión JSON del ICP y del business profile que el usuario pueda guardar.
6. Valida internamente el business profile antes de reportar que está listo.

Si necesitas acceso externo para completar el ICP (por ejemplo, un documento comercial, lista de clientes, enlace interno, o permiso para guardar en Notion), pide **una sola acción del usuario a la vez** y explícala como resultado esperado, no como comando. Mantén la entrevista en pasos pequeños: una pregunta o permiso bloqueante por turno.

## Validaciones de contrato

- `BusinessProfile` requiere `name` y `offer_summary` no vacíos.
- `ICP` requiere `name` no vacío, y al menos uno de `target_entity_types` o `fit_criteria`.
- `confidence_level` debe ser `low`, `medium` o `high`.
- `approval_status` por defecto es `draft` — un humano debe aprobarlo antes de operacionalizar.

## Estilo

- Toda la salida al usuario en **español**.
- Evita jerga genérica de SaaS gringo: usa el lenguaje del sector público colombiano (entidad, ordenador del gasto, supervisor, plan de adquisiciones, SECOP).
- No inventes cifras ni nombres de entidades. Si no hay dato, marca el gap.
- Reporta avances como resultados de negocio y siguiente acción, no como comandos ejecutados.

---

# Generación de target accounts (Historia de usuario 2)

Una vez aprobado el ICP, esta skill también guía al agente para producir una **lista priorizada de target accounts** del sector público colombiano. La salida debe poder validarse contra `TargetAccountList` del paquete `b2g_gtm_toolkit.models.gtm`.

## Cuándo usar esta sección

Actívala cuando el usuario pida:
- "Construir lista de cuentas objetivo a partir del ICP".
- "Priorizar entidades públicas para investigación SECOP".
- "Generar target accounts B2G".

## Entregable

Un archivo siguiendo `templates/target-accounts.md` que se serializa a JSON conforme a `TargetAccountList` (lista de `TargetAccount` + metadata `icp_id`, `generated_at`, `source`, `count`).

## Metodología

### Paso 1 — Tomar el ICP como insumo
Lee el ICP aprobado (segmentos, regiones, criterios de fit, descalificadores, triggers). Identifica:
- Tipos de entidad objetivo (`target_entity_types`).
- Categorías o subgrupos (`target_categories`).
- Regiones (`target_regions`).
- Criterios duros que se pueden traducir a filtros sobre datos públicos.

### Paso 2 — Enumerar entidades candidatas
Cruzar el ICP contra fuentes confiables:
- **SECOP I/II/TVEC** (datos.gov.co): entidades compradoras activas en los últimos 12–24 meses, monto contratado, modalidades predominantes, categorías UNSPSC compradas, número de procesos publicados.
- **DANE — categorización municipal**: las alcaldías se clasifican en categoría especial, 1, 2, 3, 4, 5 o 6 según ingresos corrientes de libre destinación (Ley 617/2000). Sirve para descartar municipios sin capacidad de compra.
- **Función Pública / SIGEP**: tipo de entidad, nivel (territorial vs nacional), sector administrativo, estructura.
- **DNP / Plan Anual de Adquisiciones**: PAA publicado con rubros relevantes.
- **Portales de transparencia y prensa**: cambios de directivos, nuevos planes de desarrollo, hallazgos de Contraloría.

Para cada candidata captura como mínimo: `name`, `entity_type`, `location` (departamento + municipio si aplica), `identifiers` (NIT, código DIVIPOLA cuando exista), `category` (categoría municipal o sectorial).

### Paso 3 — Calcular fit_score (0–100)
Asigna un score en 0–100 con justificación corta (`fit_rationale`). Heurística sugerida:
- +30 si el tipo de entidad coincide con `target_entity_types`.
- +20 si la ubicación coincide con `target_regions`.
- +20 si la categoría/segmento coincide con `target_categories`.
- +15 si hay evidencia de compra reciente en SECOP en la categoría afín.
- +10 si hay PAA publicado con rubros afines.
- +5 si hay trigger observable (cambio directivo, nuevo plan, hallazgo).
- −20 si dispara un descalificador del ICP (categoría 6 sin recursos, pliego atado a incumbente, etc.).

Acota el resultado a [0, 100]. Si la evidencia es débil, marca `research_status = "not_started"` y baja el score.

### Paso 4 — Definir owner y next_research_step
- `owner`: persona del equipo GTM responsable de la cuenta (texto libre o referencia a un `Owner` existente). Si no se sabe, deja vacío.
- `next_research_step`: la **próxima acción concreta** de investigación. Ejemplos:
  - "Buscar procesos SECOP II 2024–2026 con UNSPSC 81111800".
  - "Revisar PAA 2026 de la Alcaldía X".
  - "Validar vigencia de contrato del incumbente".
  - "Confirmar categoría municipal y presupuesto de inversión".

### Paso 5 — Dedupe por id estable
Cada `TargetAccount` tiene un `id` opcional. Si no se provee, el sistema deriva un id estable con `b2g_gtm_toolkit.utils.ids.stable_id(name, entity_type, location)`. La validación de `TargetAccountList` rechaza dos cuentas con el mismo id estable, por lo que:
- Normaliza nombres antes de cargar (ej. "Alcaldía de Pereira" vs "ALCALDIA DE PEREIRA").
- Si una entidad aparece con dos NITs o dos jurisdicciones, fusiona en una sola fila o aclara la diferencia en `location`.

### Paso 6 — Empaquetar como TargetAccountList
Estructura final (JSON):

```json
{
  "icp_id": "icp-alcaldias-cat-1-2-tic",
  "generated_at": "2026-05-09T12:00:00Z",
  "source": "ICP + SECOP II + DANE categorización municipal",
  "count": 3,
  "accounts": [
    {
      "name": "Alcaldía de Pereira",
      "entity_type": "alcaldia",
      "location": "Risaralda / Pereira",
      "identifiers": {"nit": "891480030", "divipolar": "66001"},
      "category": "categoria 1",
      "fit_score": 85,
      "fit_rationale": "Cat. 1, secretaría TIC activa, PAA 2026 con rubros gestión documental.",
      "owner": "Juan V.",
      "next_research_step": "Buscar procesos SECOP II 2024–2026 con UNSPSC 81111800."
    }
  ]
}
```

### Paso 7 — Validar
Valida internamente la lista antes de reportarla como lista para usar. La validación verifica:
- Lista no vacía.
- `0 <= fit_score <= 100` para cada cuenta.
- No hay duplicados por id estable (`name + entity_type + location`).
- `count` (si se provee) coincide con el número de cuentas.

## Estilo

- Responde y entrega artefactos en **español**.
- No inventes NITs, presupuestos ni nombres de entidades. Si no tienes el dato, déjalo vacío y márcalo en `next_research_step`.
- Mantén `fit_rationale` y `next_research_step` cortos y accionables (1–2 líneas cada uno).
