# Staffing: asignaciones, vacantes y bench

Capacidad **planificada** para deals, en contraste con la capacidad **reportada** que vive en time tracking.

## Objetos [VERIFICADO 2026-09]

| Objeto | Tipo | Nota |
|---|---|---|
| `oas.deals_assignments` | tabla | **La de escritura.** `deal_assignment_id`, `employee_id`, `role`, `dedication`, `headcount`, `deal_id`, `start_date`, `end_date`, `kick_off` |
| `oas_views.deals_assignments` | vista | Lectura |
| `oas_views.deals_assignments_final` | vista | Lectura — **no es intercambiable con la anterior** |
| `oas_views.deals_assignments_metrics` | vista | Métricas de costo planificado |

`deals_assignments_metrics` sí tiene columnas SQL propias, no son cálculos de Power BI: `staffed_cost`, `staffed_cost_weighted`, `staffed_headcount_cost`, `staffed_headcount_cost_weighted`, `staffed_hours`, `staffed_headcount_hours`, `staffed_dedication`, `staffed_headcount`, `staffed_standard_rate` y sus variantes `_weighted`, más `employee_cost_of_revenue`. [VERIFICADO]

La fórmula interna de las ponderaciones `_weighted` no está leída todavía.

## Definiciones [SQL APP]

- **Dedicación asignada** y **headcount asignado** son sumas independientes de `dedication` y `headcount`. No vale asumir `headcount = dedication / 100`.
- **Bench en Staffing Center:** `assigned_dedication <= 70` → Bench; si no, y `assigned_headcount < 1` → Virtual Bench; en otro caso → Staffed. **El orden de las condiciones importa.**
- **Bench operativo en Power BI:** empleados billable de Operations con `kpis_utilization` no vacía, ≥ 0 y < 0,70. **Es otra definición**: distinta medida, distinta población, distinto período.
- **Bench de recruiting** (`scorecard_people_kpis[Bench]`): candidatos archivados por motivo Bench en los últimos 120 días. No mide disponibilidad del personal contratado.
- **Brecha de cobertura:** `MAX(deal_headcount) - SUM(headcount de asignaciones con persona real)`, excluyendo nombres `Vacant%`. `COUNT(DISTINCT employee_id)` es cantidad de personas, distinta de headcount.
- **Alineación:** `Match` compara los conjuntos de proyectos del staffing vigente contra el último día reportado; **no compara los porcentajes**. `overstaffed` es dedicación asignada > 100.

**Tres definiciones de bench conviviendo.** Antes de reportar un número de bench, decir cuál de las tres.

## Reglas no obvias [SQL APP]

- Las fechas efectivas priorizan `modified_start_date` y `modified_end_date` sobre las originales.
- El bench excluye `Closed Lost`, empleados `Vacant%`, IDs desde 99999, y exige personas `Active`, billable, en Operations, Mixilo o Habit (BU 2 Mixilo Services, 3 Professional Services, 5 HABIT Services; ver `control-center-pnl.md`). La alineación usa solo Operations.
- Las vacantes se evalúan sobre lo que intersecta hoy y los próximos 30 días. Ausencia de fila no significa que el deal no exista.
- La comparación de alineación solo cubre Portfolio 1 a 5 y agrupa cuentas con FEMSA o KOF bajo una misma clave. Es una excepción implementada para esa pantalla, no una equivalencia general.
- La asignación comercial se actualiza en `hubspot.deals`, columnas `account_id` y **`projectid`** (sin guion bajo).

## Riesgos

- Equiparar los tres benches.
- Contar vacantes como personas.
- Leer `Match` como igualdad de dedicación.
- Sumar asignaciones de intervalos distintos como si fueran simultáneas.
