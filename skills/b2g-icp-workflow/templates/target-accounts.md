# Target Accounts — B2G Colombia

> Lista priorizada de entidades públicas derivada del ICP. Cada fila corresponde a un `TargetAccount` y todo el bloque debe poder serializarse como `TargetAccountList`.

## Metadata

- **ICP de referencia** (`icp_id`):
- **Fecha de generación** (`generated_at`):
- **Fuente / método** (`source`):
  *(ej. "ICP aprobado + SECOP II 2024–2026 + DANE categorización municipal")*
- **Total de cuentas** (`count`):

## Cuentas objetivo (`accounts`)

> Una fila por entidad. No inventar NITs ni presupuestos. Si falta evidencia, dejar el campo vacío y reflejarlo en `next_research_step`.

| # | name | entity_type | location (depto/mun) | category | NIT | fit_score (0–100) | fit_rationale | owner | next_research_step |
|---|------|-------------|----------------------|----------|-----|-------------------|---------------|-------|--------------------|
| 1 |      |             |                      |          |     |                   |               |       |                    |
| 2 |      |             |                      |          |     |                   |               |       |                    |
| 3 |      |             |                      |          |     |                   |               |       |                    |

## Notas de priorización

- Top 3 por `fit_score` y por qué:
  1.
  2.
  3.
- Cuentas marcadas como inciertas (evidencia débil):
- Cuentas excluidas explícitamente y motivo (descalificadores del ICP):

## Salida JSON sugerida

```json
{
  "icp_id": "",
  "generated_at": "",
  "source": "",
  "count": 0,
  "accounts": [
    {
      "name": "",
      "entity_type": "",
      "location": "",
      "category": "",
      "identifiers": {"nit": ""},
      "fit_score": 0,
      "fit_rationale": "",
      "owner": "",
      "next_research_step": ""
    }
  ]
}
```

## Validación

Validar con:

```bash
b2g-gtm validate target-accounts <ruta.json>
```

La validación rechaza listas vacías, `fit_score` fuera de [0, 100] y duplicados por id estable derivado de `(name, entity_type, location)`.
