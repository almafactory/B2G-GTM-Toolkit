# Plan de implementación: B2G-GTM-Toolkit

**ID de la funcionalidad**: `001-b2g-gtm-toolkit` | **Fecha**: 2026-05-09 | **Spec**: `spec.md`

## Resumen

Construir un toolkit B2G GTM local-first que pueda instalarse desde GitHub y ser usado tanto por Codex como por Claude Code. La primera versión se enfoca en el flujo completo de ingresos disparado manualmente: recolectar entradas base de la empresa, definir un ICP del sector público colombiano, generar insumos de investigación de cuentas objetivo, ejecutar investigación SECOP mediante scripts en lugar de navegación del agente, guardar salidas estructuradas en Notion y generar entregables para account executives como outreach, preparación de reuniones y briefs de propuesta/business case.

El enriquecimiento programado, el monitoreo de señales de compra y las alertas por Slack y email se planifican como una segunda iteración. La primera versión todavía debe modelar responsables y señales para que la capa futura de cron se pueda agregar sin rehacer el modelo central.

## Contexto técnico

**Lenguaje/Versión**: Python 3.11+ para scripts de investigación y utilidades CLI; Markdown para skills del agente y guías de flujo; JSON Schema para contratos de script.

**Dependencias principales**:
- `httpx` para acceso a APIs de SECOP/datos.gov.co.
- `pydantic` para registros normalizados y validación.
- `typer` para comandos CLI locales.
- `notion-client` para verificación y escritura en bases de datos de Notion.
- `python-dotenv` para configuración local de entorno.
- `tenacity` para manejo de reintentos en APIs externas.
- `pytest` para pruebas unitarias e integración.

**Almacenamiento**: Notion como workspace GTM durable. Archivos JSONL locales bajo `data/runs/` como logs auditables de ejecución y salida intermedia segura ante reintentos.

**Pruebas**: `pytest`, validación JSON Schema, respuestas SECOP basadas en fixtures, pruebas de dry-run de Notion y snapshot tests para briefs generados.

**Plataforma objetivo**: Workspace local de desarrollador/agente en Windows primero, pero la estructura del repo debe seguir siendo multiplataforma. El objetivo del agente es tanto Codex como Claude Code.

## Decisiones técnicas

### Empaquetado y estilo de instalación

Usar un repositorio plantilla de GitHub como producto instalable, con un paquete de skills incluido dentro del repo.

Esto nos da ambas cosas:
- un scaffold del proyecto con scripts, esquemas, pruebas, docs y configuración de entorno;
- skills orientadas al agente que se pueden copiar o enlazar en `.agents/skills` y `.claude/skills`.

Las skills por sí solas no bastan porque la investigación SECOP, la configuración de Notion, el dedupe, la validación y las ejecuciones repetibles necesitan código ejecutable y pruebas. Un repo plantilla solo tampoco basta porque los flujos GTM necesitan instrucciones de agente que guíen la recolección de entradas y la generación de salidas.

### Integración con Notion

Usar Notion como sistema de registro GTM. El toolkit incluirá un manifiesto de esquema que define bases de datos, propiedades y relaciones requeridas. Un comando de setup verifica bases existentes por nombre o por ID almacenado, crea las faltantes cuando esté autorizado y escribe los IDs resueltos de las bases en la configuración local.

Bases de datos por defecto de Notion:
- `B2G Business Profiles`
- `B2G ICPs`
- `B2G Target Accounts`
- `B2G SECOP Research`
- `B2G Opportunities`
- `B2G GTM Outputs`
- `B2G Owners`
- `B2G Signals` planificado para la iteración 2, pero el esquema se incluye en v1

La primera versión debe soportar modo dry-run de Notion para que los usuarios puedan previsualizar cambios en las bases de datos antes de escribir.

### Enfoque de scripts para la API de SECOP

El agente no debe navegar SECOP manualmente ni copiar datos al workspace. Debe llamar a un script local de investigación con entradas estructuradas y luego razonar sobre salidas normalizadas.

Las preguntas exactas que debe responder el diseño del script son:
- ¿Cuál es la entrada de búsqueda: nombre de entidad, NIT de entidad, municipio, departamento, códigos UNSPSC, keywords, modalidad, rango de fechas, valor mínimo, estado de oportunidad o nombre de proveedor/contratista?
- ¿Qué fuente se consulta: SECOP II procesos, SECOP II contratos, SECOP I procesos, SECOP I histórico, datasets SECOP integrados o JSON OCDS?
- ¿La tarea es investigación de cuenta, descubrimiento de oportunidad, reconstrucción de historial de compra, descubrimiento de competidores/proveedores o shortlist de licitaciones?
- ¿Qué límite de resultados, estrategia de paginación y ventana temporal deben aplicarse?
- ¿Qué campos se requieren para que un registro sea utilizable aguas abajo?
- ¿Cómo deben identificarse duplicados entre SECOP I, SECOP II y ejecuciones repetidas?
- ¿Qué provenance debe preservarse para que un usuario pueda rastrear los hallazgos hasta la fuente oficial?

Para v1, usar datasets abiertos de Colombia Compra Eficiente/datos.gov.co y fuentes JSON/OCDS donde encajen en el flujo. Empezar con IDs de dataset configurables en lugar de hardcodear cada endpoint en la lógica de negocio.

### Notificaciones

Slack y email son canales de notificación planificados. No deben bloquear v1 porque los cron jobs, el enriquecimiento y el monitoreo de señales son de la iteración 2. El modelo de datos de v1 debe incluir campos de owner, preferencia de notificación y prioridad de señal para que la capa de notificación se pueda añadir limpiamente.

### Alcance de la primera versión

V1 incluye:
- flujo de entrada para business profile y definición de ICP;
- generación de target accounts desde el ICP;
- script de investigación SECOP para ejecuciones manuales;
- verificación y almacenamiento del esquema de Notion;
- flujos de salida para outreach, preparación de reuniones y briefs de propuesta/business case.

V1 excluye:
- cron jobs programados;
- enriquecimiento continuo;
- notificaciones automáticas de señales de compra;
- fuentes de contratación multi-país;
- UI completa más allá de CLI y flujos de agente.

## Estructura del proyecto

### Documentación

```text
.sdd/specs/001-b2g-gtm-toolkit/
├── spec.md
├── plan.md
├── data-model.md
├── tasks.md
└── contracts/
    └── secop-research-output.schema.json
```

### Código fuente

```text
src/b2g_gtm_toolkit/
├── cli.py
├── config.py
├── models/
│   ├── business.py
│   ├── gtm.py
│   ├── notion.py
│   └── secop.py
├── secop/
│   ├── client.py
│   ├── datasets.py
│   ├── normalize.py
│   ├── research.py
│   └── dedupe.py
├── notion/
│   ├── schema.py
│   ├── verify.py
│   └── write.py
├── outputs/
│   ├── outreach.py
│   ├── meeting_prep.py
│   └── proposal_brief.py
└── utils/
    ├── ids.py
    └── logging.py

skills/
├── b2g-icp-workflow/
├── b2g-secop-research/
├── b2g-notion-gtm-os/
└── b2g-output-workflows/

schemas/
├── notion-workspace.schema.json
├── secop-research-input.schema.json
└── secop-research-output.schema.json

tests/
├── unit/
├── integration/
└── fixtures/
```

## Resumen del modelo de datos

| Entidad | Atributos principales | Relaciones |
|--------|--------------------|---------------|
| Business Profile | name, offer, competitors, customers, stage, constraints | Tiene muchos ICPs |
| ICP | segment, fit criteria, disqualifiers, triggers, committee, confidence | Pertenece a Business Profile; tiene muchas Target Accounts |
| Target Account | name, entity type, location, identifiers, fit score, owner | Pertenece a ICP; tiene muchos Research Records y Opportunities |
| SECOP Research Record | source, source id, process id, contract id, object, value, dates, buyer, supplier, provenance | Pertenece a Target Account; puede crear Opportunity |
| Opportunity | title, status, value, deadline, modality, fit score, next action | Pertenece a Target Account; referencia Research Records |
| GTM Output | type, title, content, source records, approval status | Pertenece a Account u Opportunity |
| Owner | name, role, email, slack id, notification preferences | Posee Accounts, Opportunities, Signals |
| Signal | type, priority, source, summary, detected at, action status | Pertenece a Account u Opportunity; pertenece a Owner |

## Resumen de contratos API

Este es un toolkit local de CLI/script, no una web API en v1.

| Comando | Propósito |
|---------|---------|
| `b2g-gtm init` | Crear config local, verificar variables de entorno y preparar carpetas |
| `b2g-gtm notion verify` | Revisar las bases de datos y relaciones requeridas de Notion |
| `b2g-gtm notion setup --dry-run` | Previsualizar la creación o actualización requerida de bases de datos de Notion |
| `b2g-gtm secop research --input <file>` | Ejecutar investigación SECOP a partir de criterios estructurados de ICP/cuenta |
| `b2g-gtm notion sync --run <run-id>` | Guardar en Notion los resultados de investigación normalizados |
| `b2g-gtm output create --type <type> --source <id>` | Generar outreach, preparación de reunión o brief de propuesta a partir de datos guardados/investigados |

## Fases de implementación

1. **Setup**: skeleton del paquete, CLI, config, ejemplo de env, documentación del repo y carpetas del skill-pack para Codex y Claude Code.
2. **Modelos fundacionales**: modelos Pydantic para business profile, ICP, account, registros de investigación SECOP, oportunidades, manifiestos de bases de datos Notion y salidas GTM.
3. **Workspace de Notion**: manifiesto de esquema, verificador, setup en dry-run y helpers de escritura/actualización.
4. **Script de investigación SECOP**: cliente de dataset configurable, contrato de entrada, paginación, normalización, dedupe, captura de provenance y salida JSONL de ejecución.
5. **Skills del agente**: skill de flujo ICP, workflow de investigación SECOP, workflow de Notion GTM OS y skills de salida.
6. **Generación de salidas**: builders deterministas de contexto y templates para outreach, preparación de reunión y briefs de propuesta/business case.
7. **Verificación**: fixtures, pruebas unitarias, dry-runs de integración y un smoke test que complete la entrada ICP hasta una salida de investigación lista para Notion.

## Riesgos y restricciones

- Los nombres de campos de SECOP/datos.gov.co pueden variar entre datasets, así que el mapeo de dataset debe quedar aislado en configuración y pruebas.
- Los registros SECOP pueden estar duplicados o ser inconsistentes, así que el dedupe y el provenance son requisitos de primera clase.
- La configuración de relaciones en Notion puede ser frágil si los usuarios renombraran propiedades; los IDs de base de datos deben guardarse después de la verificación.
- Las salidas del agente no deben inventar hechos de contratación. El flujo debe preservar los registros fuente y marcar con claridad la evidencia faltante.
- Las notificaciones por Slack/email se difieren de forma intencional, pero los campos de owner y signal deben estar presentes ya en el esquema.

## Referencias externas

- Colombia Compra Eficiente lista datasets abiertos de SECOP a través de datos.gov.co, incluyendo contratos/procesos SECOP II y datasets SECOP I.
- Colombia Compra Eficiente también publica datos SECOP JSON/OCDS, útiles para registros de contratación respaldados por fuentes oficiales.
