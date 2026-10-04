# Entidades y relaciones

## Deal (HubSpot)

- **Tabla**: `hubspot.deals` — 1.471 filas
- **ID**: `deal_id` (bigint, id nativo de HubSpot)
- **Qué es**: una oportunidad comercial. Es la fuente del revenue proyectado.
- **Columnas relevantes**: `dealname`, `amount`, `closedate`, `createdate`, `dealstage`, `dealtype`, `headcount`, `length_of_contract`, `kickoff_date`, `kick_of_yet`, `pricing_structure`, `line_item_revenue`, `conversion_rate_manual`, `hubspot_owner_id`, `company_id`, `account_id`, `projectid`
- **Bloque de sales** (prefijo `sls_`): `sls_campaign`, `sls_deal_region`, `sls_lead_identified`, `sls_lead_prospected`, `sls_meeting_scheduled`, `sls_meeting_completed`, `sls_meeting_source`, `sls_mkt_driven`, `sls_sdr`, `sls_type_of_meeting`. Sirven para funnel de generación de demanda.
- **Joins**: `hubspot_owner_id` → `deals_owners.owner_id`; `company_id` → `deals_companies.company_id`; `dealstage` → `deals_stages.hubspot`; `dealtype` → `deals_types.hubspot`

`line_item_revenue = true` cambia el origen del cálculo: el revenue de ese deal se deriva de sus line items, no del `amount` del deal.

## Project (OAS)

- **Vista**: `oas_views.projects_joined`
- **ID**: `project_id`
- **Qué es**: proyecto en ejecución. Aporta revenue vía `pipeline.manual_revenue`.
- Un deal puede apuntar a un proyecto por `hubspot.deals.projectid`.

## Account y Client

- **Account**: unidad de facturación. `account_id` aparece en `hubspot.deals`, `pipeline.budget`, `pipeline.retention_target`, `pipeline.revenue_commit_q3`.
- **Client**: empresa madre. Un client agrupa varias accounts. `view_revenue` expone ambos como texto (`client`, `account`) resueltos por COALESCE entre proyecto y deal.
- `oas_views.client_revenue_mix` liga `client_id` + `year` a un `mix_id` (mix de revenue por cliente).

## Company (firmográficos)

- **Tabla**: `hubspot.deals_companies` — 996 filas
- **ID**: `company_id`
- **Columnas**: `company`, `industry`, `city`, `country`, `number_of_employees`, `annual_revenue`, `data_maturity_level`, `is_public`, `website`, `linkedin`, `logo_url`, `type`
- Útil para segmentar revenue por industria, país o tamaño de cliente.

## Owner

- **Tabla**: `hubspot.deals_owners` — 37 filas
- **Columnas**: `owner_id`, `owner_email`, `owner_full_name`, `owner_archived`
- Filtrar `owner_archived = false` para listas de owners activos.

---

## Cómo se unifican deal y project en el revenue

`pipeline.view_revenue` resuelve el origen con estas columnas:

| Columna | Significado |
|---|---|
| `is_hubspot` | `deal_id IS NOT NULL` — la fila viene de un deal |
| `is_project` | `project_id IS NOT NULL` — la fila viene de un proyecto |
| `related_id` | `COALESCE(project_id, deal_id)` — identificador unificado |
| `related` | `COALESCE(project, deal)` — nombre unificado |
| `client`, `account` | resueltos por COALESCE entre proyecto y deal |

Para agrupar revenue por "cosa que lo genera" sin importar el origen, usar `related_id` / `related`. Para cortar solo pipeline comercial, filtrar `is_hubspot = true`.

---

## Catálogo de stages

| stage_id | stage | stage_order | valor en HubSpot |
|---|---|---|---|
| 10 | Target Leads | (null) | Target Leads |
| 1 | Open Deal | 2 | appointmentscheduled |
| 2 | In Analysis | 3 | qualifiedtobuy |
| 5 | Proposal Sent | 4 | presentationscheduled |
| 4 | Decision Maker Bought-In | 5 | decisionmakerboughtin |
| 3 | Contract Negotiation | 6 | contractsent |
| 11 | Committed | 7 | 1239606448 |
| 6 | Closed Won | 8 | closedwon |
| 7 | Closed Lost | 1 | closedlost |

`deals_stages` también tiene columnas `mixilo` y `north_america`, que mapean el mismo stage a otros pipelines de HubSpot.

`Target Leads` (10) no viene de HubSpot: son cargas manuales, y por eso tiene tasa de conversión 100 en los tres escenarios.

## Catálogo de types

| type_id | type | valor en HubSpot |
|---|---|---|
| 1 | New | newbusiness |
| 2 | Renewal | renovationbusiness |
| 3 | XSell | xsellbusiness |
| 4 | Upsell | existingbusiness |

Agrupación habitual: New + XSell = revenue nuevo; Renewal + Upsell = revenue sobre base instalada. **Confirmar con Augusto si esa es la agrupación que usa el negocio.**
