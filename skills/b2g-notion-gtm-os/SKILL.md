---
name: b2g-notion-gtm-os
description: Verificar, planificar y sincronizar el workspace GTM B2G en Notion sin escrituras destructivas en V1.
version: 1.0.0
language: es
---

# B2G Notion GTM OS

Esta skill orquesta la integración entre el toolkit B2G GTM y un workspace de Notion que actúa como sistema operativo GTM. La premisa es **dry-run primero**: nunca se escribe en Notion sin confirmación explícita y un token válido.

## Flujo recomendado

1. **Verify**
   - Ejecuta `b2g-gtm notion verify`.
   - El comando recorre las 8 bases requeridas (`B2G Business Profiles`, `B2G ICPs`, `B2G Target Accounts`, `B2G SECOP Research`, `B2G Opportunities`, `B2G GTM Outputs`, `B2G Owners`, `B2G Signals`) y reporta:
     - bases ausentes
     - propiedades faltantes
     - propiedades con tipo incorrecto
     - relaciones sin destino configurado
   - Si no hay `NOTION_TOKEN`, el comando corre contra un cliente stub que reporta el workspace como vacío.

2. **Setup (dry-run)**
   - Ejecuta `b2g-gtm notion setup --dry-run`.
   - Imprime un plan con tres secciones: bases a crear, bases a actualizar, sin cambios.
   - `--apply` está reservado para iteraciones futuras y devuelve un error claro en V1.

3. **Sync de investigación**
   - Ejecuta `b2g-gtm notion sync --run <run-id>`.
   - Carga `data/runs/<run-id>/secop-research.jsonl` (producido por la skill SECOP) y mapea cada registro a propiedades de la base `B2G SECOP Research`.
   - Por defecto el comando es dry-run y muestra los upserts planeados (clave de dedupe = `Source Record ID`).
   - `--apply` está bloqueado en V1 hasta que se implemente la capa de escritura real.

4. **Revisión humana**
   - Toda página con campo `Approval Status` debe revisarse manualmente antes de pasar de `draft` a `approved`.
   - Las relaciones (ICP → Business Profile, Target Account → ICP, SECOP Research → Target Account, Opportunity → Target Account, Signal → Owner) se rellenan después de que las páginas relacionadas existan.

## Configuración recomendada (.env)

Tras crear las bases en Notion, guarda los IDs devueltos como variables de entorno:

```
NOTION_TOKEN=secret_...
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

## Limitaciones de V1

- No se ejecutan escrituras reales contra la API de Notion: `--apply` falla con un mensaje explícito.
- El cliente real (`notion-client`) sólo se importa cuando `NOTION_TOKEN` está definido.
- Los tests usan un fake client; nunca se hacen llamadas de red.
