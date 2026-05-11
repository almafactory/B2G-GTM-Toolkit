---
name: b2g-notion-gtm-os
description: Verificar, crear y sincronizar el workspace GTM B2G en Notion con dry-run primero y escrituras explícitas.
version: 1.0.0
language: es
---

# B2G Notion GTM OS

Esta skill orquesta la integración entre el toolkit B2G GTM y un workspace de Notion que actúa como sistema operativo GTM. La premisa es **dry-run primero**: nunca se escribe en Notion sin confirmación explícita, un token válido y una página compartida con la integración.

Cuando el usuario no sea técnico, no le muestres comandos por defecto. Guíalo en términos de Notion UI: crear/reutilizar integración, compartir la página, pasar la URL de la página y autorizar al agente a configurar el workspace.

Si falta un permiso externo, pide **una sola acción del usuario a la vez** y espera el resultado antes de avanzar. Ejemplo: primero pregunta si ya existe una integración de Notion; sólo después pide crearla o compartir la página; sólo después pide la URL/token que falte. No mezcles varios pasos de navegador, permisos y credenciales en un mismo mensaje salvo que el usuario pida una checklist completa.

## Flujo recomendado

1. **Verify**
   - Ejecuta `b2g-gtm notion verify`.
   - El comando recorre las 8 bases requeridas (`B2G Business Profiles`, `B2G ICPs`, `B2G Target Accounts`, `B2G SECOP Research`, `B2G Opportunities`, `B2G GTM Outputs`, `B2G Owners`, `B2G Signals`) y reporta:
     - bases ausentes
     - propiedades faltantes
     - propiedades con tipo incorrecto
     - relaciones sin destino configurado
   - Si no hay `NOTION_TOKEN`, el comando corre contra un cliente stub que reporta el workspace como vacío.

2. **Setup**
   - Ejecuta `b2g-gtm notion setup --dry-run`.
   - Imprime un plan con tres secciones: bases a crear, bases a actualizar, sin cambios.
   - Ejecuta `b2g-gtm notion setup --apply` sólo cuando el usuario haya confirmado que quiere crear/actualizar el workspace.
   - Tras aplicar, ejecuta `b2g-gtm notion verify` y sólo reporta éxito si todas las bases quedan en OK.

3. **Sync de investigación**
   - Ejecuta `b2g-gtm notion sync --run <run-id>`.
   - Carga `data/runs/<run-id>/secop-research.jsonl` (producido por la skill SECOP) y mapea cada registro a propiedades de la base `B2G SECOP Research`.
   - Por defecto el comando es dry-run y muestra los upserts planeados (clave de dedupe = `Source Record ID`).
   - Ejecuta `b2g-gtm notion sync --run <run-id> --apply` sólo con token válido y workspace verificado.
   - Reporta cuántos registros fueron creados y cuántos actualizados. No digas que hay datos en Notion antes de ver ese resultado.

4. **Revisión humana**
   - Toda página con campo `Approval Status` debe revisarse manualmente antes de pasar de `draft` a `approved`.
   - Las relaciones (ICP → Business Profile, Target Account → ICP, SECOP Research → Target Account, Opportunity → Target Account, Signal → Owner) se rellenan después de que las páginas relacionadas existan.

## Configuración recomendada (.env)

Tras crear las bases en Notion, guarda los IDs devueltos como variables de entorno:

```
NOTION_TOKEN=secret_...
NOTION_PARENT_PAGE_ID=...
NOTION_DB_B2G_BUSINESS_PROFILES=...
NOTION_DB_B2G_ICPS=...
NOTION_DB_B2G_TARGET_ACCOUNTS=...
NOTION_DB_B2G_SECOP_RESEARCH=...
NOTION_DB_B2G_OPPORTUNITIES=...
NOTION_DB_B2G_GTM_OUTPUTS=...
NOTION_DB_B2G_OWNERS=...
NOTION_DB_B2G_SIGNALS=...
```

El nombre de la variable se construye como `NOTION_DB_<NOMBRE_DE_LA_BASE>` con espacios reemplazados por guiones bajos y mayúsculas.

## Reglas de UX

- No digas "fixture", "stub", "dry-run" u "offline" a usuarios no técnicos sin traducirlo.
- Di "datos de ejemplo incluidos en el proyecto" cuando se use la corrida local de prueba.
- Di "vista previa; no se escribió nada" cuando se use dry-run.
- Cuando un permiso de Notion bloquee el flujo, pide una sola acción concreta y descríbela en lenguaje de la UI de Notion.
- No repitas tokens en respuestas.
- Si un token fue pegado en chat, recomienda rotarlo antes de usarlo en producción.
- Si Notion falla por permisos, la primera hipótesis debe ser: la página no fue compartida con la integración.

## Nota técnica para mantenedores

La API reciente de Notion expone propiedades y queries por `data_sources`. El CLI debe usar data source IDs para verificar propiedades, actualizar esquemas, consultar registros y crear páginas.
