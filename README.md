# B2G GTM Toolkit

Toolkit local-first para equipos B2G colombianos que venden al sector publico. Convierte contexto del negocio en un ICP, lista de cuentas objetivo, investigacion en SECOP y entregables comerciales (outreach, preparacion de reunion, brief de propuesta), todo guardado en Notion como sistema GTM persistente.

## Alcance MVP

- Definir un ICP B2G a partir del contexto del contratista.
- Generar una lista priorizada de cuentas objetivo del sector publico.
- Ejecutar investigacion repetible sobre datos abiertos de SECOP / datos.gov.co.
- Verificar y sincronizar resultados en un workspace de Notion.
- Generar briefs para account executives: outreach, preparacion de reunion y propuesta/business case.

Pendiente para iteracion 2: cron jobs, enriquecimiento continuo y notificaciones automaticas por Slack y email.

## Instalacion

Requiere Python 3.11+.

```bash
git clone <repo-url>
cd "SECOP tool"
python -m venv .venv
source .venv/Scripts/activate   # Git Bash en Windows
pip install -e .
cp .env.example .env
```

Edita `.env` con tu token de Notion, IDs del workspace y, opcionalmente, tu app token de datos.gov.co.

## Primer uso

### Camino recomendado: agente guiado

Si no eres técnico, no necesitas operar la terminal. Pídele al agente algo como:

- "Conecta este toolkit a Notion"
- "Ensayemos el toolkit con datos de ejemplo"
- "Corre investigación SECOP y guarda el resultado en Notion"
- "Genera outreach para esta oportunidad"

El agente debe encargarse de instalar dependencias, configurar `.env`, verificar Notion, correr las validaciones y explicar los resultados en lenguaje simple. La guía de onboarding sin jerga técnica está en `docs/non-technical-onboarding.md`.

### Camino técnico: CLI

Despues de `pip install -e .` el comando `b2g-gtm` queda disponible. Si prefieres correr sin instalar, usa `PYTHONPATH=src python -m b2g_gtm_toolkit.cli ...`.

Quick-start MVP (sin red, todo con fixtures locales):

```bash
b2g-gtm validate business-profile examples/business-profile.json
b2g-gtm validate target-accounts examples/target-accounts.json
b2g-gtm secop research --input examples/secop-research-input.json --offline
b2g-gtm notion verify
b2g-gtm notion setup --dry-run
b2g-gtm notion setup --apply
b2g-gtm notion sync --run <run-id> --apply
b2g-gtm output create --type outreach --source examples/opportunity.json
```

`--offline` usa datos de ejemplo incluidos en el repo, sin consultar servicios externos. `b2g-gtm notion verify` regresa exit code 1 cuando aun no hay un workspace creado o configurado. `notion setup --dry-run` imprime el plan sin escribir, `notion setup --apply` crea/actualiza las bases requeridas con confirmación explícita y `notion sync --apply` escribe registros reales en Notion cuando hay credenciales válidas.

Las salidas crudas de cada ejecucion quedan en `data/runs/<run-id>/secop-research.jsonl` con su `manifest.json`.

## Compatibilidad con agentes

El toolkit esta pensado para usarse desde agentes de codificacion como Codex y Claude Code. Las skills viven en `skills/` y pueden enlazarse a `.claude/skills/` o a la carpeta de skills de Codex usando los scripts en `scripts/` (proximas fases). El CLI cubre el flujo manual cuando se usa directamente.

## Estructura

- `src/b2g_gtm_toolkit/` - paquete Python con CLI, modelos, cliente SECOP y helpers de Notion.
- `schemas/` - JSON Schemas de entrada/salida.
- `skills/` - skills de agente para los flujos GTM.
- `data/runs/` - logs auditables de cada ejecucion local.
- `.sdd/specs/001-b2g-gtm-toolkit/` - spec, plan y tareas.

## Iteracion 2 - automatizacion pendiente

V1 deja el modelo de datos listo (owners, senales, preferencias de notificacion, prioridad y estados) pero **no envia notificaciones**. Las siguientes capacidades quedan diferidas para iteracion 2:

- **Enriquecimiento por cron**: jobs programados que refresquen cuentas objetivo, oportunidades y senales SECOP sin intervencion manual.
- **Notificaciones por Slack**: empuje de senales de prioridad alta/urgente al canal o DM correspondiente segun `Owner.slack_id` y `notification_preferences.slack`.
- **Notificaciones por email**: alertas a `Owner.email` cuando `notification_preferences.email` esta activo, con resumenes diarios o por evento.

Mientras tanto, el toolkit registra `notification_status` en `pending`/`not_sent` y deja la senal lista para que un planificador externo la consuma cuando se habilite la iteracion 2.
