# Uso del B2G GTM Toolkit con agentes

Este documento explica como instalar el paquete de skills B2G y usarlo desde **Claude Code** o **Codex** sobre el mismo repositorio. Las skills son carpetas con un `SKILL.md` y plantillas que el agente carga para guiar el flujo GTM completo: ICP, target accounts, investigacion SECOP, sync con Notion y entregables para Account Executives.

## Principio de UX

El usuario no técnico no debería operar la terminal. Los comandos de este documento son una referencia interna para agentes y mantenedores. Cuando el usuario pida un resultado de negocio ("conecta Notion", "ensayemos el toolkit", "genera outreach"), el agente debe ejecutar los pasos necesarios y explicar sólo:

- qué necesita del usuario;
- qué se verificó;
- qué se creó o actualizó;
- cuál es el siguiente paso de negocio.

Para el flujo sin jerga técnica, ver [`docs/non-technical-onboarding.md`](./non-technical-onboarding.md). Para lecciones aprendidas de fricción real, ver [`docs/ux-friction-log.md`](./ux-friction-log.md).

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
| `b2g-notion-gtm-os` | Verificar workspace de Notion, planificar setup, importar workflows locales y escribir investigacion SECOP en Notion. | "verificar Notion", "sync GTM en Notion" |
| `b2g-output-workflows` | Generar outreach, meeting prep y propuesta/business case desde oportunidades o cuentas en Notion. | "generar outreach", "preparar reunion AE", "armar business case" |

## 3. Comandos CLI subyacentes para agentes

Las skills llaman a `b2g-gtm` (Typer). Estos comandos son internos: úsalos desde el agente, no como instrucciones que el usuario debe copiar por defecto.

```bash
b2g-gtm init
b2g-gtm validate business-profile examples/business-profile.json
b2g-gtm validate target-accounts examples/target-accounts.json
b2g-gtm secop research --input examples/secop-research-input.json
b2g-gtm notion verify
b2g-gtm notion setup --dry-run
b2g-gtm notion setup --apply
b2g-gtm secop research --input examples/secop-research-input.json --to-notion --apply
b2g-gtm notion import-workflow --business-profile examples/business-profile.json --icp examples/icp.json --target-accounts examples/target-accounts.json --run <run-id> --apply
b2g-gtm notion sync --run <run-id>
b2g-gtm notion sync --run <run-id> --apply
b2g-gtm output create --type outreach     --opportunity-page <notion-page-id> --to-notion --apply
b2g-gtm output create --type meeting-prep --opportunity-page <notion-page-id> --to-notion --apply
b2g-gtm output create --type proposal     --target-account-page <notion-page-id> --to-notion --apply
```

## 4. Walkthrough interno end-to-end (MVP)

Asumiendo el repo clonado, dependencias instaladas y `.env` configurado segun `.env.example`:

1. **Instala las skills para tu agente** (paso 1).
2. **Define el ICP** invocando `b2g-icp-workflow` y compartiendo `examples/business-profile.json`. La skill produce un brief tipo `examples/icp.json`.
3. **Genera target accounts** con la misma skill (segunda fase). Toma como referencia `examples/target-accounts.json`.
4. **Investiga SECOP** internamente y escribe el resultado en Notion cuando el usuario lo autorice:
   ```bash
   b2g-gtm secop research --input examples/secop-research-input.json --to-notion --apply
   ```
   El resultado de negocio queda en `B2G SECOP Research`. Los archivos bajo `data/runs/` son artefactos locales de auditoria, importacion o diagnostico.
5. **Verifica, crea o importa en Notion** con la skill `b2g-notion-gtm-os`:
   ```bash
   b2g-gtm notion verify
   b2g-gtm notion setup --dry-run
   b2g-gtm notion setup --apply
   b2g-gtm notion import-workflow --business-profile examples/business-profile.json --icp examples/icp.json --target-accounts examples/target-accounts.json --run <run-id> --apply
   ```
6. **Crea entregables para AE** desde una oportunidad o cuenta objetivo de Notion:
   ```bash
   b2g-gtm output create --type outreach --opportunity-page <notion-page-id> --to-notion --apply
   b2g-gtm output create --type meeting-prep --opportunity-page <notion-page-id> --to-notion --apply
   b2g-gtm output create --type proposal --target-account-page <notion-page-id> --to-notion --apply
   ```

Cada paso se puede ensayar con los archivos de `examples/` antes de usar datos reales. En flujos reales, Notion es el estado canonico y los archivos locales son preview, importacion, pruebas o diagnostico. Al explicar esto a un usuario no técnico, di "datos de ejemplo incluidos con el proyecto", no "fixtures" ni "offline". Para el mapa visual de este flujo, ver `docs/workflows.md`.

## 5. Reinstalar tras actualizar las skills

Cuando edites cualquier `skills/*/SKILL.md` o plantilla, vuelve a correr el script con `-Force`:

```powershell
pwsh scripts/install-claude-skills.ps1 -Force
pwsh scripts/install-codex-skills.ps1 -Force
```

Sin `-Force` el script avisa que el destino difiere y no toca nada — util para detectar cambios manuales en los destinos.
