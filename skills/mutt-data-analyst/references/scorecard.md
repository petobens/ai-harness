# Scorecard: KPIs manuales y staffing semanal

Schema `scorecard`, que alimenta la app de Scorecard en Appsmith (migrada desde
Power BI). El Scorecard mira métricas **semanales**.

## KPIs manuales [VERIFICADO 2026-10-30]

Son los KPIs que no salen de otra tabla y se cargan a mano: Sales, Operations,
Finance, Mixilo y Marketing.

| Objeto | Qué tiene |
|---|---|
| `scorecard.manual_kpis` | Catálogo: `kpi_key`, `area`, `label`, `unit` (`number`, `ratio`, `pct`, `usd`), `target_rule`, `scorecard_agg`, `sort_order`, `active` |
| `scorecard.manual_values` | Valor semanal: `week_start_date`, `kpi_key`, `value`, `updated_by`, `updated_at` |
| `scorecard.manual_weeks` | Asigna cada semana a un único `scorecard_month` |
| `scorecard.manual_targets` | Target mensual por KPI (ver la advertencia de abajo) |
| `scorecard.view_manual_weekly` | Formato ancho: una fila por semana, una columna por KPI y otra `<kpi>_target` |
| `oas.scorecard_manual` | **Vista de compatibilidad** que hoy lee del schema `scorecard`. Para análisis nuevos, ir a `scorecard.*` |

Dos reglas por KPI definen cómo se pasa de semana a mes:

- **`scorecard_agg`**: cómo se agrega el mes. `sum` suma las semanas (llamados,
  leads, reuniones). `last` toma la última semana del mes (todos los de Finance:
  cash to expenses, delayed invoicing, overdue payments).
  **Nunca promediar un KPI `last`.**
- **`target_rule`**: cómo se lleva el target mensual a la semana. `divide` lo
  reparte entre las semanas del mes; `repeat` aplica el mismo valor a cada
  semana.
- **El mes de una semana sale de `manual_weeks`**, no de
  `date_trunc('month', week_start_date)`: una semana que cruza dos meses
  pertenece a uno solo.
- Filtrar `active = true` en el catálogo.

**Targets del Scorecard:** `manual_targets` y `scorecard.kpi_targets` existen,
pero no están validados como objetivos de la compañía. No reportarlos como
targets corporativos ni usarlos para semáforos sin confirmarlo con Augusto. Los
targets confirmados están en `control-center-pnl.md`.

## Staffing semanal [VERIFICADO 2026-10-30]

`scorecard.mv_staffing_weekly` agrega `oas_views.deals_assignments_metrics` por
semana, mes, empleado y `related_id`, con `employee_cost_of_revenue`. Columnas:
`staffed_hours`, `staffed_headcount_hours`, `staffed_cost_weighted`,
`staffed_headcount_cost_weighted`, `staffed_standard_rate_weighted`,
`staffed_headcount_standard_rate_weighted`.

- **Es capacidad planificada (staffing), no horas reportadas.** No la uses como
  utilización real.
- **Agrupa por semana *y* por mes**: una semana que cruza dos meses aparece en
  dos filas. Para el total semanal, sumar por `week_start` sin `month_start`.
- Cubre solo el año en curso (desde la semana que contiene el 1° de enero).
- Los `_weighted` heredan la ponderación de `deals_assignments_metrics`: full
  weighted, sin umbral de 60 (ver `staffing.md`).

## Reglas del Scorecard [confirmadas por Augusto, 2026-09]

- Secciones: Company, Sales & Mkt, Ops, Mixilo, HABIT, People, Finance.
- Delivery utilization es cross company y va en Company. En Ops, solo delivery
  utilization de Ops y billable de Ops; lo mismo por departamento en Mixilo y
  HABIT.
- Las métricas de staffing van solo en Ops: es el único departamento que staffea
  deals.
- En People: biweekly status (NPS = % green − % red), 1:1s, exit interviews y
  people talks. Nada del Pulse Survey.
