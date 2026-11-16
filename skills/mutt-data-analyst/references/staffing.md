# Staffing: asignaciones, vacantes y bench

Capacidad **planificada** para deals, en contraste con la capacidad
**reportada** que vive en time tracking.

## Objetos [VERIFICADO 2026-09]

| Objeto | Tipo | Nota |
|---|---|---|
| `oas.deals_assignments` | tabla | **La de escritura.** `deal_assignment_id`, `employee_id`, `role`, `dedication`, `headcount`, `deal_id`, `start_date`, `end_date`, `kick_off` |
| `oas_views.deals_assignments` | vista | Lectura |
| `oas_views.deals_assignments_final` | vista | Lectura — **no es intercambiable con la anterior** |
| `oas_views.deals_assignments_metrics` | vista | Métricas de costo planificado |

`deals_assignments_metrics` sí tiene columnas SQL propias, no son cálculos de
Power BI: `staffed_cost`, `staffed_cost_weighted`, `staffed_headcount_cost`,
`staffed_headcount_cost_weighted`, `staffed_hours`, `staffed_headcount_hours`,
`staffed_dedication`, `staffed_headcount`, `staffed_standard_rate` y sus
variantes `_weighted`, más `employee_cost_of_revenue`. [VERIFICADO]

### Cómo calcula `deals_assignments_metrics` [VERIFICADO 2026-10-06]

- **Grano diario** (empleado × deal × día hábil), sin Closed Lost.
- **Tres fuentes:** `oas_views.deals_assignments`; vacantes de
  `oas_views.deals_vacants`, con costo fijo 4.000, standard rate 8.000 y 8 h; y
  `oas_views.manual_revenue_assignments` (proyectos), con tasa 100.
- **`staffed_cost` diario** = salario × `dedication`/100 / días hábiles del mes,
  redondeado a entero. El salario es el último de `finance.view_salary_cost`
  hasta ese mes, si no el último disponible, si no el standard cost del step.
- **`_weighted`** = métrica × tasa / 100. La tasa es 100 si el deal tiene
  kickoff y el día es anterior al fin del mes en curso; si no,
  `pipeline.deals_info.realistic_rate`, que es la
  **tasa de la matriz sin override manual y sin umbral de 60**.

Consecuencia: el costo staffeado ponderado equivale a **full weighted**, no al
Forecast. Un deal con tasa 25 aporta 25% de su costo aunque aporte 0 al
`realistic_amount`, y un `conversion_rate_manual` se ignora. No comparar
`_weighted` contra `realistic_amount` sin aclararlo.

## Definiciones [SQL APP]

- **Dedicación asignada** y **headcount asignado** son sumas independientes de
  `dedication` y `headcount`. No vale asumir `headcount = dedication / 100`.
- **Bench en Staffing Center:** `assigned_dedication <= 70` → Bench; si no, y
  `assigned_headcount < 1` → Virtual Bench; en otro caso → Staffed.
  **El orden de las condiciones importa.**
- **Bench operativo en Power BI:** empleados billable de Operations con
  `kpis_utilization` no vacía, ≥ 0 y < 0,70. **Es otra definición**: distinta
  medida, distinta población, distinto período.
  - **MBR Report** (2026-10) usa la misma idea: utilización < 70% del mes, Ops
    billable activos a fin de mes, **M3 y S3 excluidos**, con el departamento y
    el billable actuales (como el Power BI). Agosto 2026 daba 13 contra 9 del
    deck, por reclasificaciones posteriores al freeze.
- **Bench de recruiting del Scorecard** (`scorecard_people_kpis[Bench]`, hoy
  sobre `lever.pbi_scorecard_opportunities`): candidatos distintos archivados
  por motivo `Bench` en los 120 días hasta el cierre. No mide disponibilidad del
  personal contratado.
- **Current Bench de Lever** (Talent Center, acordado con Talent): candidatos
  cuyo último archivo de bench tiene motivo `Bench`, sin ventana de fecha. Una
  oportunidad posterior no los saca. Ver `lever.md` § Bench.
- **Brecha de cobertura:**
  `MAX(deal_headcount) - SUM(headcount de asignaciones con persona real)`,
  excluyendo nombres `Vacant%`. `COUNT(DISTINCT employee_id)` es cantidad de
  personas, distinta de headcount.
- **Alineación:** `Match` compara los conjuntos de proyectos del staffing
  vigente contra el último día reportado; **no compara los porcentajes**.
  `overstaffed` es dedicación asignada > 100.

**Cuatro definiciones de bench conviviendo**: dos de Mutters contratados
(Staffing Center por asignación; Power BI / MBR por utilización) y dos de
candidatos (Scorecard 120 días; Current Bench de Lever). Antes de reportar un
número de bench, decir cuál.

## Reglas no obvias [SQL APP]

- Las fechas efectivas priorizan `modified_start_date` y `modified_end_date`
  sobre las originales.
- El bench excluye `Closed Lost`, empleados `Vacant%`, IDs desde 99999, y exige
  personas `Active`, billable, en Operations, Mixilo o Habit (BU 2 Mixilo
  Services, 3 Professional Services, 5 HABIT Services; ver
  `control-center-pnl.md`). La alineación usa solo Operations.
- Las vacantes se evalúan sobre lo que intersecta hoy y los próximos 30 días.
  Ausencia de fila no significa que el deal no exista.
- La comparación de alineación solo cubre Portfolio 1 a 5 y agrupa cuentas con
  FEMSA o KOF bajo una misma clave. Es una excepción implementada para esa
  pantalla, no una equivalencia general.
- La asignación comercial se actualiza en `hubspot.deals`, columnas `account_id`
  y **`projectid`** (sin guion bajo).

## Foto de staffing de hoy

[SQL APP MBR Report · Presentation › Ops, VERIFICADO 2026-11-06]

Asientos de trabajo con clientes a hoy: asignaciones + vacantes próximas.

- **Asignaciones**: `oas_views.deals_assignments` con `status = 'Active'`,
  `stage <> 'Closed Lost'`, `start_date <= hoy` (o NULL) y `end_date >= hoy` (o
  NULL).
- **Vacantes**: `oas_views.deals_vacants` (unido a `oas_views.deals`) sin Closed
  Lost, que arrancan en ≤ 30 días y no terminaron.
- **Portfolio y director**: `oas_views.accounts_joined.area` y `director`.
  **`director` es un nombre**: se resuelve contra
  `bamboo.employees_joined.employee`. La mayoría de los directores reporta al
  COO; hay excepciones (p. ej. Portfolio 4 → Marian, HABIT / Mixilo → CEO).
- Al 2026-11-06: 136 Mutters, 136,2 FTE, 31 cuentas, 47 deals, 27 vacantes.
- Es información interna de staffing: no sumarla a un organigrama abierto a toda
  la empresa (ver `people.md` § Organigrama).

## Modelo nuevo: schema `staffing` [EN CONSTRUCCIÓN — VERIFICADO 2026-10-30]

Lo está armando el equipo de Augusto para reemplazar el staffing por deal con un
modelo de **posiciones**. La estructura cambió por completo entre el 13/10 y el
30/10, así que
**no usarlo para métricas ni compararlo con `oas.deals_assignments`** sin
confirmar con Augusto, y leer las columnas antes de cada consulta.

Conceptos a hoy:

- **`positions`**: posición por deal o proyecto, con rol, step mínimo, inglés
  mínimo, fluidez US, `hc`, bill rate y moneda, fase y continuidad
  (`continues_position_id`).
- **`assignments`**: persona (o placeholder, o candidato de Lever) en una
  posición, con `status`, `dedication`, fechas y `tentative_until`.
  `assignment_interviews` registra entrevistas con el cliente.
- **`position_requests`**: pedidos de posición generados desde los deals, que se
  revisan y aprueban (`approved_position_id`). `position_request_requirements` y
  `position_requirements` piden capacidades con nivel mínimo e importancia.
- **Taxonomía de capacidades extendida**: `capabilities_ext`, `practices_ext` y
  `capability_terms` (sinónimos), que apuntan a las oficiales de `development`.
- **Perfil de proyectos desde ClickUp**: `project_profile_people`,
  `project_profile_capabilities`, `project_industries` y `evidence_levels`.
- **`v_demand_without_supply`**: capacidades pedidas en deals que hoy no tienen
  oferta.

## Riesgos

- Usar el schema `staffing` como fuente vigente.
- Equiparar las cuatro definiciones de bench.
- Contar vacantes como personas.
- Leer `Match` como igualdad de dedicación.
- Sumar asignaciones de intervalos distintos como si fueran simultáneas.
