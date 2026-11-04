# Schema `pipeline`

## `pipeline.view_revenue` (vista) — fuente de verdad

29 columnas. Construida sobre `pipeline.revenue` con joins a
`oas_views.projects_joined`, `oas_views.deals`, `hubspot.deals_types`,
`hubspot.deals_stages`, `hubspot.conversion_rates` y
`oas_views.client_revenue_mix`.

| Columna | Notas |
|---|---|
| `revenue_id` | solo para filas de `manual_revenue`; NULL para deals |
| `project_id`, `deal_id` | mutuamente excluyentes |
| `date` | día hábil |
| `amount` | monto sin ponderar |
| `type`, `stage`, `type_id`, `stage_id` | resueltos contra catálogos |
| `client`, `account`, `project`, `deal`, `logo_url` | COALESCE proyecto/deal |
| `is_project`, `is_hubspot`, `related_id`, `related` | origen unificado |
| `pessimistic_rate`, `realistic_rate`, `optimistic_rate` | enteros 0–100 |
| `pessimistic_amount`, `realistic_amount`, `optimistic_amount` | monto × tasa / 100 |
| `headcount`, `realistic_headcount` | headcount nominal y ponderado |
| `realistic_amount_old`, `realistic_rate_old` | cálculo previo, sin umbral 60 |
| `mix_id` | mix de revenue del cliente para el año |

## `pipeline.revenue` (vista)

`manual_revenue` UNION ALL `deals_revenue`. Grano diario. Columnas:
`revenue_id`, `deal_id`, `project_id`, `date`, `amount`, `type_id`, `stage_id`,
`headcount`, `kickoff`.

Las filas manuales llegan con `kickoff = true` y `headcount` NULL.

## `pipeline.deals_revenue` (vista)

Prorratea el monto de cada deal sobre los días hábiles del período. Lógica: por
cada mes del deal calcula días hábiles trabajados sobre días hábiles del mes
(`fraction`), normaliza por la suma de fracciones del deal (`months_equiv`),
reparte el total y luego divide por día hábil.

Filtros embebidos: `stage_id IS NOT NULL`, `stage_id <> 7`, `line_item_revenue`
false o NULL, y `date >= 2024-01-01`. Después une `line_items_revenue` con los
mismos cortes.

## `pipeline.line_items_revenue` (vista)

Reparte el monto de cada line item de forma pareja entre sus días hábiles.
Ajusta `start_date` y `end_date` que caen en fin de semana hacia el viernes
anterior. Filtra `stage <> 'Closed Lost'` y `line_item_revenue = true`.

## `pipeline.manual_revenue` (tabla, 392 filas)

Carga manual de revenue por proyecto. Columnas: `revenue_id`, `project_id`,
`date`, `amount`, `type_id`, `stage_id`. `pipeline.manual_audit` (529 filas)
registra los cambios con `change_type` y `change_date`. `view_manual_audit` los
expone enriquecidos.

## Materializadas

| Objeto | Filas | Contenido |
|---|---|---|
| `view_revenue_mv` | ~40k | copia de `view_revenue` |
| `revenue_monthly_mv` | ~2.4k | agregado mensual: `month_start`, `period` (YYYYMM), `project_id`, `deal_id`, `related_id`, `unweighted_revenue`, `revenue` |
| `retention_target_monthly_mv` | 420 | target de retención mensual |

En `revenue_monthly_mv`, `revenue` es la suma de `realistic_amount` y
`unweighted_revenue` la de `amount`. Usa `project_id_key` / `deal_id_key` con -1
en lugar de NULL para agrupar.

## Snapshots [VERIFICADO 2026-09-28]

- `revenue_versions`: snapshot de `view_revenue` por `version_date`.
  **Es la tabla de análisis** (Pipeline Evolution). [VERIFICADO 2026-10-30]
  Versiones desde 2025-12-15, **semanales, los jueves** (workflow "DB:
  PipelineVersions", 11 h de Buenos Aires; `version_date` queda en 14:00 UTC);
  ~40–45k filas cada una. `version_date` es timestamp: castear `::date` para
  filtrar por día. No trae `headcount` ni `mix_id`.
  **Filtrar siempre `version_date` y `date`.**
- `revenue_versions_changes` (vista): diferencias entre versiones.
- `revenue_versions_pbi` (vista): formato para Power BI.
- `revenue_versions_weekly` **ya no existe en la base.** Si aparece en código o
  documentación vieja, no usarla (era solo un depósito de datos).

## Budget y targets

- `retention_target` (420 filas) y `retention_target_monthly_mv`: **en uso**
  (Ops Retention Target, Control Center). Solo Ops (Professional Services, BU
  3), por definición: las otras BU no tienen target. Ene–dic 2026, total 10,5M.
  [VERIFICADO 2026-09-28] Ver `metrics.md`.
- `budget_revenue` (120 filas), `budget` (vacía), `view_budget_revenue_daily`:
  sin uso. No incluirlos salvo pedido explícito.

## Commit

- **Fuente vigente: los planes `commit` de `simulation_revenue`**
  (`revenue_plans`, `revenue_plan_months`, `revenue_plan_lines`). Cubren Q1 a Q4
  2026. Reglas y SQL en `metrics.md` § Forecast vs commit. [VERIFICADO
  2026-10-30]
- `pipeline.revenue_commit_q3` (`period`, `deal_id`, `account_id`, `project_id`,
  `amount`): baseline de Jul–Sep 2026. Coincide al peso con el plan de Q3.
- `revenue_commit` (el commit rolling) **ya no existe en la base.** [VERIFICADO
  2026-09-28]

## Simulación

**Commit Simulation usa el schema `simulation_revenue`** [VERIFICADO
2026-09-28]:

| Objeto | Para qué |
|---|---|
| `simulation_revenue.revenue_scenarios` | Cabecera: `simulation_id`, `simulation_name`, `status`, `start_period`, `end_period`, `created_by/at`, `closed_by/at`, `snapshot_at`, `snapshot_origin_id`, `revision`, `note` |
| `simulation_revenue.revenue_scenario_monthly` | Líneas × mes de una simulación: montos base, `manual_amount`, `simulation_amount`, `current_amount`, overrides `auto_*`, `is_removed`, `is_user_edited`, `edited_by/at` |
| `simulation_revenue.revenue_scenario_sources` | Fuentes de revenue disponibles para simular |
| `simulation_revenue.revenue_simulation_source_monthly` | Pipeline vivo por fuente y mes (`current_amount`, `unweighted_amount`) para comparar |
| `simulation_revenue.revenue_plans`, `revenue_plan_months`, `revenue_plan_lines` | Planes promovidos (hoy, los commits por trimestre). Ver § Commit |
| `simulation_revenue.revenue_admins`, `revenue_viewers` | Listas de acceso de la app (`email`, `added_at`, `added_by`) |
| `revenue_scenario_create(name, start, end, email, base_id)` | Función: crea una simulación (opcionalmente copiando otra) |
| `revenue_scenario_mutate(id, revision, action, payload jsonb, email)` | Función: aplica un cambio; `revision` es control de concurrencia |

Las tablas `pipeline.revenue_simulations`, `revenue_simulation_lines`,
`revenue_simulation_months` y las vistas `pipeline.revenue_simulation_*`
**ya no existen**: todo se movió a `simulation_revenue`. [VERIFICADO 2026-09-28]

`revenue_scenario_monthly` y `revenue_scenario_sources` son vistas;
`revenue_scenarios` y `revenue_scenario_comments` son tablas. Funciones del
schema: `revenue_scenario_create`, `_mutate`, `_allocate`, `_allocate_pipeline`,
`_comment`, `_config`, `_guard`, `_note`, `_recalculate`, `_recalculate_v2`.
Escribir siempre a través de ellas, nunca directo a las tablas.

## Otras vistas

- `deals_info` (53 columnas): deal enriquecido con montos por escenario, fechas,
  headcount asignado, costo, margen, rate estándar. Base de `deals_revenue`.
- `line_items_info` (26 columnas): equivalente para line items.
- `projects_revenue_share_monthly`: participación de cada proyecto en el revenue
  mensual.
- `view_revenue_ale` (14 columnas): recorte alternativo de revenue.
  **Confirmar para qué se usa.**
