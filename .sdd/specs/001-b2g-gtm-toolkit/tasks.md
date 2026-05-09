# Tareas: B2G-GTM-Toolkit

**ID de la funcionalidad**: `001-b2g-gtm-toolkit`
**Prerrequisitos**: `spec.md`, `plan.md`, `data-model.md`

## Formato

```text
- [ ] T001 [P] [US1] Description with file path
```

- `[P]`: Puede ejecutarse en paralelo cuando las dependencias ya están satisfechas.
- `[US#]`: La tarea pertenece a una historia de usuario de `spec.md`.

---

## Fase 1: Setup

**Propósito**: Crear el scaffold instalable local-first del toolkit.

- [X] T001 Crear el esqueleto del paquete Python en `src/b2g_gtm_toolkit/` con `__init__.py`, `cli.py`, `config.py` y subcarpetas del paquete.
- [X] T002 Crear los metadatos del proyecto y la configuración de dependencias en `pyproject.toml` para Python 3.11+, Typer, Pydantic, httpx, notion-client, python-dotenv, tenacity, pytest y jsonschema.
- [X] T003 Crear `.env.example` con placeholders para Notion, datos.gov.co/SECOP, Slack, email y ruta local de salida.
- [X] T004 Crear carpetas locales por defecto `data/runs/`, `schemas/`, `skills/` y `tests/fixtures/`.
- [X] T005 Agregar el entrypoint CLI `b2g-gtm` con comandos placeholder en `src/b2g_gtm_toolkit/cli.py`.
- [X] T006 Actualizar `README.md` con alcance MVP, enfoque de instalación, setup local, compatibilidad con agentes y flujo de primer uso.
- [X] T007 [P] Agregar entradas en `.gitignore` para `.env`, salidas locales de ejecución, caches, entornos virtuales y exports temporales de Notion.

**Checkpoint**: El paquete se instala localmente y `b2g-gtm --help` puede ejecutarse.

---

## Fase 2: Modelos fundacionales y contratos

**Propósito**: Definir estructuras de datos compartidas usadas por todos los flujos MVP.

**Bloqueante**: Completar antes de implementar las historias de usuario.

- [X] T008 Crear modelos Pydantic de business e ICP en `src/b2g_gtm_toolkit/models/business.py`.
- [X] T009 Crear modelos de GTM para account, opportunity, owner, signal y output en `src/b2g_gtm_toolkit/models/gtm.py`.
- [X] T010 Crear modelos de entrada SECOP, raw record, normalized research record, relevance y provenance en `src/b2g_gtm_toolkit/models/secop.py`.
- [X] T011 Crear el manifiesto de bases de datos de Notion y modelos de propiedades en `src/b2g_gtm_toolkit/models/notion.py`.
- [X] T012 Crear helpers de ID estable, normalización, hashing y timestamps en `src/b2g_gtm_toolkit/utils/ids.py`.
- [X] T013 Crear una configuración de logging estructurado en `src/b2g_gtm_toolkit/utils/logging.py`.
- [X] T014 Agregar JSON Schema para la entrada de investigación SECOP en `schemas/secop-research-input.schema.json`.
- [X] T015 Copiar o generar el schema de salida de investigación SECOP en `schemas/secop-research-output.schema.json` desde `.sdd/specs/001-b2g-gtm-toolkit/contracts/secop-research-output.schema.json`.
- [X] T016 Agregar el schema del manifiesto del workspace de Notion en `schemas/notion-workspace.schema.json`.
- [X] T017 [P] Agregar pruebas unitarias para validación de modelos y campos requeridos en `tests/unit/test_models.py`.
- [X] T018 [P] Agregar pruebas unitarias para IDs estables, normalización de texto y hashing de payload en `tests/unit/test_ids.py`.

**Checkpoint**: Los modelos centrales validan payloads de ejemplo de business profile, ICP, target account, registro SECOP, opportunity, owner, signal y output.

---

## Fase 3: Historia de usuario 1 - Definir un ICP B2G a partir de contexto real de cliente (P1)

**Meta**: Guiar a los usuarios por las entradas base y producir un brief B2G ICP utilizable.

**Prueba independiente**: Proporcionar un contexto de contratista de ejemplo y verificar que el toolkit produzca un ICP con tipos de entidad, criterios de ajuste, descalificadores, disparadores, roles del comité de compra, señales observables y confianza.

### Implementation

- [X] T019 [US1] Crear la carpeta de la skill del flujo ICP en `skills/b2g-icp-workflow/`.
- [X] T020 [US1] Escribir `skills/b2g-icp-workflow/SKILL.md` usando `E:\skills\ventas\gtm-icp-definition.md` como metodología base.
- [X] T021 [US1] Agregar la plantilla de entrada de business profile en `skills/b2g-icp-workflow/templates/business-profile.md`.
- [X] T022 [US1] Agregar la plantilla de salida de ICP en `skills/b2g-icp-workflow/templates/icp-brief.md`.
- [X] T023 [US1] Implementar el comando local de validación de business profile en `src/b2g_gtm_toolkit/cli.py`.
- [X] T024 [P] [US1] Agregar un fixture de ejemplo de business profile en `tests/fixtures/business-profile.sample.json`.
- [X] T025 [US1] Agregar pruebas que validen el business profile de ejemplo y los payloads ICP en `tests/unit/test_icp_workflow_contract.py`.

**Checkpoint**: Un agente puede usar la skill para pedir entradas faltantes y producir un brief ICP que pase el contrato del modelo.

---

## Fase 4: Historia de usuario 2 - Construir una lista de target accounts a partir del ICP (P1)

**Meta**: Convertir el ICP en una lista priorizada de cuentas o segmentos de cuentas del sector público.

**Prueba independiente**: Usar un ICP completado y verificar que el toolkit devuelva target accounts con justificación de ajuste y siguientes pasos de investigación.

### Implementation

- [X] T026 [US2] Crear la guía de generación de target accounts dentro de `skills/b2g-icp-workflow/SKILL.md`.
- [X] T027 [US2] Agregar la plantilla de lista de target accounts en `skills/b2g-icp-workflow/templates/target-accounts.md`.
- [X] T028 [US2] Implementar la validación de payload de target accounts en `src/b2g_gtm_toolkit/models/gtm.py`.
- [X] T029 [US2] Agregar validación CLI para archivos de target accounts en `src/b2g_gtm_toolkit/cli.py`.
- [X] T030 [P] [US2] Agregar un fixture de ejemplo de target accounts en `tests/fixtures/target-accounts.sample.json`.
- [X] T031 [US2] Agregar pruebas para claves de dedupe de cuentas y límites de fit score en `tests/unit/test_target_accounts.py`.

**Checkpoint**: Una lista generada de target accounts puede validarse y usarse como entrada para investigación SECOP.

---

## Fase 5: Historia de usuario 3 - Investigar oportunidades SECOP e historial de compra (P1)

**Meta**: Ejecutar investigación SECOP repetible basada en scripts y producir registros normalizados con provenance.

**Prueba independiente**: Proporcionar criterios de target account o ICP y verificar que el script de investigación escriba una salida JSONL normalizada válida.

### Implementation

- [X] T032 [US3] Crear el registro configurable de datasets SECOP en `src/b2g_gtm_toolkit/secop/datasets.py`.
- [X] T033 [US3] Implementar el cliente HTTP de datos.gov.co/SECOP con paginación, reintentos y parámetros de consulta en `src/b2g_gtm_toolkit/secop/client.py`.
- [X] T034 [US3] Implementar funciones de normalización SECOP en `src/b2g_gtm_toolkit/secop/normalize.py`.
- [X] T035 [US3] Implementar la estrategia de dedupe de SECOP en `src/b2g_gtm_toolkit/secop/dedupe.py`.
- [X] T036 [US3] Implementar la orquestación de investigación en `src/b2g_gtm_toolkit/secop/research.py`.
- [X] T037 [US3] Agregar el comando `b2g-gtm secop research --input <file>` en `src/b2g_gtm_toolkit/cli.py`.
- [X] T038 [US3] Escribir la salida normalizada de la ejecución en `data/runs/<run-id>/secop-research.jsonl`.
- [X] T039 [P] [US3] Agregar fixtures de respuestas raw de SECOP en `tests/fixtures/secop/`.
- [X] T040 [US3] Agregar pruebas unitarias para normalización, dedupe y provenance en `tests/unit/test_secop_research.py`.
- [X] T041 [US3] Agregar prueba de contrato validando la salida contra `schemas/secop-research-output.schema.json` en `tests/contract/test_secop_output_schema.py`.

**Checkpoint**: La investigación SECOP puede ejecutarse desde una entrada estructurada y producir salida válida según esquema, deduplicada y con provenance preservada.

---

## Fase 6: Historia de usuario 4 - Guardar inteligencia GTM en Notion (P1)

**Meta**: Verificar o preparar el workspace GTM de Notion y sincronizar registros investigados.

**Prueba independiente**: Ejecutar una verificación dry-run del esquema requerido de Notion y validar que los registros de investigación se mapeen a los payloads esperados de las bases de datos de Notion.

### Implementation

- [X] T042 [US4] Definir el manifiesto por defecto del workspace de Notion en `src/b2g_gtm_toolkit/notion/schema.py`.
- [X] T043 [US4] Implementar la verificación de bases de datos de Notion en `src/b2g_gtm_toolkit/notion/verify.py`.
- [X] T044 [US4] Implementar el planificador de setup dry-run de Notion en `src/b2g_gtm_toolkit/notion/verify.py`.
- [X] T045 [US4] Implementar helpers de escritura/actualización de Notion en `src/b2g_gtm_toolkit/notion/write.py`.
- [X] T046 [US4] Agregar el comando `b2g-gtm notion verify` en `src/b2g_gtm_toolkit/cli.py`.
- [X] T047 [US4] Agregar el comando `b2g-gtm notion setup --dry-run` en `src/b2g_gtm_toolkit/cli.py`.
- [X] T048 [US4] Agregar el comando `b2g-gtm notion sync --run <run-id>` en `src/b2g_gtm_toolkit/cli.py`.
- [X] T049 [US4] Crear la carpeta de la skill de workflow de Notion en `skills/b2g-notion-gtm-os/`.
- [X] T050 [US4] Escribir `skills/b2g-notion-gtm-os/SKILL.md` describiendo verificación, dry-run, sync y flujo de revisión.
- [X] T051 [P] [US4] Agregar pruebas para el mapeo de propiedades de Notion en `tests/unit/test_notion_schema.py`.
- [X] T052 [US4] Agregar pruebas de integración dry-run con respuestas simuladas de Notion en `tests/integration/test_notion_verify.py`.

**Checkpoint**: El toolkit puede verificar la preparación del esquema de Notion y preparar payloads de sync sin requerir escrituras reales durante las pruebas.

---

## Fase 7: Historia de usuario 5 - Generar entregables para account executives (P2)

**Meta**: Convertir la inteligencia almacenada/investigada en briefs de outreach, preparación de reuniones y propuesta/business case.

**Prueba independiente**: Seleccionar un fixture de oportunidad investigada y generar los tres tipos de salida con referencias a fuentes.

### Implementation

- [X] T053 [US5] Crear la carpeta de la skill de workflow de salida en `skills/b2g-output-workflows/`.
- [X] T054 [US5] Escribir `skills/b2g-output-workflows/SKILL.md` usando skills de ventas para soporte de outreach, preparación de reuniones, calificación y propuesta/business case.
- [X] T055 [US5] Implementar el builder de contexto de outreach en `src/b2g_gtm_toolkit/outputs/outreach.py`.
- [X] T056 [US5] Implementar el builder de contexto de preparación de reunión en `src/b2g_gtm_toolkit/outputs/meeting_prep.py`.
- [X] T057 [US5] Implementar el builder de contexto de propuesta/business case en `src/b2g_gtm_toolkit/outputs/proposal_brief.py`.
- [X] T058 [US5] Agregar plantillas de salida en `skills/b2g-output-workflows/templates/`.
- [X] T059 [US5] Agregar el comando `b2g-gtm output create --type <type> --source <id>` en `src/b2g_gtm_toolkit/cli.py`.
- [X] T060 [P] [US5] Agregar un fixture de oportunidad investigada en `tests/fixtures/opportunity.sample.json`.
- [X] T061 [US5] Agregar snapshot tests para el contexto generado de outreach, preparación de reunión y propuesta/business case en `tests/unit/test_outputs.py`.

**Checkpoint**: Una oportunidad investigada puede producir entregables para AE respaldados por fuentes.

---

## Fase 8: Historia de usuario 6 - Preparar la base de monitoreo de owners y signals (P2, lista para iteración 2)

**Meta**: Incluir la forma de datos y los límites del workflow para un futuro enriquecimiento por cron, Slack y email sin implementar automatización en V1.

**Prueba independiente**: Validar registros de owner y signal y confirmar que el estado de notificación de señales puede representarse sin enviar notificaciones.

### Implementation

- [X] T062 [US6] Asegurar que los modelos de owner y signal incluyan Slack ID, email, preferencia de notificación, prioridad, estado de acción y estado de notificación en `src/b2g_gtm_toolkit/models/gtm.py`.
- [X] T063 [US6] Incluir `B2G Owners` y `B2G Signals` en el manifiesto del esquema de Notion en `src/b2g_gtm_toolkit/notion/schema.py`.
- [X] T064 [US6] Agregar notas de iteración 2 para notificaciones por cron, Slack y email en `README.md`.
- [X] T065 [P] [US6] Agregar pruebas de validación de owner y signal en `tests/unit/test_signals.py`.

**Checkpoint**: El toolkit puede almacenar datos listos para owner/signal, mientras que las notificaciones programadas reales siguen diferidas.

---

## Fase 9: Instalación del paquete de skills del agente

**Propósito**: Hacer que los flujos sean utilizables por Codex y Claude Code desde el mismo repositorio.

- [X] T066 Crear script de instalación para carpetas de skills de Codex en `scripts/install-codex-skills.ps1`.
- [X] T067 Crear script de instalación para carpetas de skills de Claude Code en `scripts/install-claude-skills.ps1`.
- [X] T068 Agregar docs de uso multiagente en `docs/agent-usage.md`.
- [X] T069 Agregar un mapa de workflow que muestre ICP -> target accounts -> investigación SECOP -> sync con Notion -> salidas en `docs/workflows.md`.
- [X] T070 [P] Agregar archivos de entrada de ejemplo end-to-end en `examples/`.

**Checkpoint**: Un usuario puede instalar el skill pack para cualquiera de los dos agentes y seguir el workflow MVP documentado.

---

## Fase 10: Verificación end-to-end y pulido

**Propósito**: Validar el flujo MVP y ajustar la documentación antes de considerar completa la implementación.

- [X] T071 Agregar un smoke test de entrada ICP de ejemplo a salida de investigación SECOP usando fixtures en `tests/integration/test_mvp_smoke.py`.
- [X] T072 Agregar un smoke test de salida SECOP a payload dry-run de Notion en `tests/integration/test_research_to_notion.py`.
- [X] T073 Agregar un smoke test de fixture de oportunidad a contexto de salida AE en `tests/integration/test_output_workflow.py`.
- [X] T074 Ejecutar la suite completa de pruebas y corregir fallos.
- [X] T075 Revisar la claridad de los docs para usuario B2G en español primero en `README.md`, `docs/workflows.md` y archivos de skills.
- [X] T076 Marcar como completadas las tareas de implementación de este archivo a medida que se hagan.

**Checkpoint**: MVP can be demonstrated locally without live SECOP or Notion dependencies by using fixtures and dry-run mode.

---

## Dependencias

- **Fase 1** debe terminar antes de que el trabajo de implementación pueda correr limpio.
- **Fase 2** bloquea todas las fases de historias de usuario porque define contratos compartidos.
- **Fase 3** debería terminar antes de la Fase 4 porque los target accounts dependen del workflow de ICP.
- **Fase 4** debería terminar antes de la Fase 5 porque la investigación SECOP consume criterios de cuenta.
- **Fase 5** y **Fase 6** pueden avanzar en paralelo después de la Fase 2 si sus contratos están estables.
- **Fase 7** depende de la salida de investigación de la Fase 5 y de los modelos de salida GTM de la Fase 2.
- **Fase 8** puede avanzar después del trabajo de esquema de las Fases 2 y 6.
- **Fase 9** puede avanzar después de que existan las primeras versiones de las skills.
- **Fase 10** depende de todas las fases MVP.

## Ejemplos de ejecución paralela

After Phase 2:

```text
T032-T041 SECOP research script
T042-T052 Notion workspace integration
T053-T061 output workflow generation
```

Within Phase 5:

```text
T032 dataset registry
T034 normalization
T035 dedupe
T039 fixtures
```

Within Phase 7:

```text
T055 outreach context
T056 meeting prep context
T057 proposal/business-case context
T058 output templates
```

## Corte MVP

El MVP está completo cuando T001-T061 y T066-T075 están hechos. T062-T065 se incluyen porque mantienen el esquema de Notion listo para la iteración 2, pero no se requiere comportamiento de envío por cron, Slack o email para V1.
