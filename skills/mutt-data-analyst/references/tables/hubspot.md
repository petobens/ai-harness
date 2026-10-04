# Schema `hubspot`

Réplica de HubSpot en Postgres. Portal ID **22714877**; URL de un deal: `https://app.hubspot.com/contacts/22714877/deal/{deal_id}`.

## `hubspot.deals` (1.471 filas, 40 columnas)

Ver `references/entities.md` para el detalle de columnas.

Campos que cambian el cálculo de revenue:

| Columna | Efecto |
|---|---|
| `conversion_rate_manual` | override de tasa; gana sobre la matriz |
| `line_item_revenue` | si es true, el revenue sale de los line items |
| `kick_of_yet`, `kickoff_date` | alimentan el flag `kickoff` que fuerza tasa 100 en meses pasados y el corriente |
| `pricing_structure` | modalidad de facturación |
| `length_of_contract`, `headcount` | dimensionamiento |

## `hubspot.line_items` (890 filas)

`line_item_id`, `line_item`, `amount`, `price`, `quantity`, `start_date`, `end_date`, `deal_id`, `description`, `vuriltek_invoice_id`, `sas_invoice_id`. Los dos últimos enlazan con facturación (schemas `vuriltek` y `sas`).

`line_items_inconsistencies` (vista) detecta line items mal cargados — revisarla antes de confiar en un total por deal.

## Catálogos

- `deals_stages` (9 filas), `deals_types` (4 filas): ver `entities.md`.
- `deals_owners` (37 filas): dueños de deals.
- `deals_companies` (996 filas): firmográficos.
- `conversion_rates` (36 filas): matriz stage × type con las tres tasas.

## Histórico y auditoría

- `deal_stages_record` (4.386 filas) + `view_deal_stages_record`: histórico de pasos por stage. Base para velocity y tiempo en etapa.
- `deals_audit` (23.844 filas) + `view_deals_audit`, `view_audits`: cambios sobre deals.
- `conversion_rate_empiric`, `view_empiric_conversion_rate_ps`: tasas de conversión observadas, para contrastar con las teóricas.
- `meetings`: reuniones, con el bloque `sls_` de deals arma el funnel de generación de demanda.

## No usar

- `deals_backup` (50.399 filas) y `line_items_backup` (42.348 filas): respaldos históricos, no reflejan el estado actual.
- `deals_insert_preview`: staging de inserción.

## Vistas seguras

`deal_safe_view` (10 columnas) expone un subconjunto de campos del deal. **Confirmar si es la vista que deben usar las apps con acceso restringido** — si es así, preferirla sobre `hubspot.deals` en cualquier app con usuarios de permisos acotados.
