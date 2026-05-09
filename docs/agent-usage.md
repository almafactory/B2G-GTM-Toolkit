# Uso del B2G GTM Toolkit con agentes

Este documento explica como instalar el paquete de skills B2G y usarlo desde **Claude Code** o **Codex** sobre el mismo repositorio. Las skills son carpetas con un `SKILL.md` y plantillas que el agente carga para guiar el flujo GTM completo: ICP, target accounts, investigacion SECOP, sync con Notion y entregables para Account Executives.

## 1. Instalar el skill pack

Los scripts de instalacion copian las carpetas de `skills/` al directorio que cada agente espera. Son **idempotentes**: si el destino ya tiene el mismo contenido, se omite; si difiere, advierten y requieren `-Force` para sobrescribir.

### Claude Code

```powershell
pwsh scripts/install-claude-skills.ps1 -Force
```

Destino: `.claude/skills/`. Reinicia Claude Code en este repo y las skills aparecen disponibles para invocacion.

### Codex

```powershell
pwsh scripts/install-codex-skills.ps1 -Force
```

Destino: `.agents/skills/`. Codex carga el directorio del proyecto al iniciar la sesion.

### Verificacion rapida

```powershell
Test-Path .claude/skills/b2g-icp-workflow/SKILL.md
Test-Path .agents/skills/b2g-icp-workflow/SKILL.md
```

Si ambos devuelven `True`, los dos agentes estan listos.

## 2. Skills disponibles

| Skill | Proposito | Trigger sugerido |
|---|---|---|
| `b2g-icp-workflow` | Construir / pressure-test ICP B2G y derivar target accounts. | "definir ICP B2G", "construir lista de cuentas objetivo" |
| `b2g-notion-gtm-os` | Verificar workspace de Notion, planificar setup dry-run, sincronizar resultados de investigacion. | "verificar Notion", "sync GTM en Notion" |
| `b2g-output-workflows` | Generar outreach, meeting prep y propuesta/business case desde una oportunidad investigada. | "generar outreach", "preparar reunion AE", "armar business case" |

## 3. Comandos CLI subyacentes

Las skills llaman a `b2g-gtm` (Typer). Los comandos principales:

```bash
b2g-gtm init
b2g-gtm validate business-profile examples/business-profile.json
b2g-gtm validate target-accounts examples/target-accounts.json
b2g-gtm secop research --input examples/secop-research-input.json
b2g-gtm notion verify
b2g-gtm notion setup --dry-run
b2g-gtm notion sync --run <run-id>
b2g-gtm output create --type outreach     --source examples/opportunity.json
b2g-gtm output create --type meeting-prep --source examples/opportunity.json
b2g-gtm output create --type proposal     --source examples/opportunity.json
```

## 4. Walkthrough end-to-end (MVP)

Asumiendo el repo clonado, dependencias instaladas (`pip install -e .`) y `.env` configurado segun `.env.example`:

1. **Instala las skills para tu agente** (paso 1).
2. **Define el ICP** invocando `b2g-icp-workflow` y compartiendo `examples/business-profile.json`. La skill produce un brief tipo `examples/icp.json`.
3. **Genera target accounts** con la misma skill (segunda fase). Toma como referencia `examples/target-accounts.json`.
4. **Investiga SECOP**:
   ```bash
   b2g-gtm secop research --input examples/secop-research-input.json
   ```
   Esto escribe `data/runs/<run-id>/secop-research.jsonl`.
5. **Verifica y sincroniza Notion** con la skill `b2g-notion-gtm-os`:
   ```bash
   b2g-gtm notion verify
   b2g-gtm notion setup --dry-run
   b2g-gtm notion sync --run <run-id>
   ```
6. **Crea entregables para AE** desde una oportunidad investigada:
   ```bash
   b2g-gtm output create --type outreach     --source examples/opportunity.json
   b2g-gtm output create --type meeting-prep --source examples/opportunity.json
   b2g-gtm output create --type proposal     --source examples/opportunity.json
   ```

Cada paso se puede ensayar con los archivos de `examples/` antes de usar datos reales. Para el mapa visual de este flujo, ver `docs/workflows.md`.

## 5. Reinstalar tras actualizar las skills

Cuando edites cualquier `skills/*/SKILL.md` o plantilla, vuelve a correr el script con `-Force`:

```powershell
pwsh scripts/install-claude-skills.ps1 -Force
pwsh scripts/install-codex-skills.ps1 -Force
```

Sin `-Force` el script avisa que el destino difiere y no toca nada — util para detectar cambios manuales en los destinos.
