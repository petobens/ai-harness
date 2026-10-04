# Control Center: delivery, utilización y P&L por proyecto

## La fuente canónica [VERIFICADO 2026-09]

**`time_tracking.view_project_metrics_monthly` es la definición oficial del P&L por proyecto.** La materializada `time_tracking.mv_project_metrics_monthly` es un passthrough exacto de esa vista, sin agregarle nada.

Esto resuelve la contradicción entre pantallas: cuando el DAX del Power BI y el JavaScript de Appsmith calculan completion o realization distinto, **manda esta vista**. Las otras dos son recálculos de respaldo para cuando no llega el valor precalculado.

Grano: una fila por mes × `account_id` × `related_key` (proyecto o deal). `row_key` es el md5 de esa combinación.

**[VERIFICADO 2026-10-01] Ni la vista ni la MV tienen columna `period`.** El mes es `month_start` (date), con `year`, `quarter` y `month`. Para cruzar con las tablas de `finance` usar `to_char(month_start, 'YYYYMM')::int`. El margen bruto se llama `gross_profit_margin`, no `gross_margin`.

## Fórmulas del P&L [VERIFICADO — leídas de la definición de la vista]

```
delivery_gross_profit  = revenue - delivery_cost - staffed_delivery_cost_forecast - delivery_expenses
gross_profit           = delivery_gross_profit - cor_expenses_allocated - cor_hr_cost_allocated
operating_income       = gross_profit - overhead_cost - operating_expenses_allocated - operating_hr_cost_allocated

<cada>_margin          = <cada resultado> / revenue        -- NULL si revenue = 0

delivery_margin_multiplier = revenue / (delivery_cost + staffed_delivery_cost_forecast + delivery_expenses)
target_revenue             = (delivery_cost + staffed_delivery_cost_forecast + delivery_expenses) * 2.5
completion                 = revenue / target_revenue
realization                = revenue / assigned_standard_rate
```

Puntos que importan:

- **El 2,5 es el factor de `target_revenue` y está hardcodeado en la vista.** No es una configuración de pantalla ni un objetivo por área: es la definición vigente de completion. Si cambia el objetivo, cambia la vista.
- **Los tres resultados son acumulativos**, cada uno resta una capa más. `delivery_gross_profit` no es `gross_profit`.
- **`staffed_delivery_cost_forecast` entra en el costo de delivery**, junto con el costo reportado. No es una alternativa al reportado, se suman.
- **El staffed forecast toma desde el mes en curso inclusive** (`period >= mes de CURRENT_DATE`). El mes actual mezcla horas reportadas con staffing planificado y cambia todos los días: un número del mes en curso no es reproducible de un día para otro. [VERIFICADO 2026-10-01]
- **Todos los márgenes son fracciones 0–1**, ya divididas por revenue. No volver a dividir por 100.
- **Los márgenes son NULL cuando revenue es 0**, no cero. Un promedio de márgenes que ignore eso miente.
- Recalcular un margen agregado siempre sobre los totales, nunca promediando los márgenes de cada fila.

## HR cost allocated: cómo se arma el pool [VERIFICADO 2026-10-01]

Leído de `finance.hr_costs_monthly`, `finance.hr_costs_to_prorate_monthly` y de la vista del P&L.

**1. Costo de HR por departamento y mes** (`finance.hr_costs_monthly.hr_cost`):

```
hr_cost = total_compensation_cost      -- compensations.paid_and_payroll_salaries
        + capitalization               -- employee_salary_impact_recovery, con signo negativo
        + bonus_reversal               -- employee_bonus_recovery, con signo negativo
        + cost_transfer                -- employee_cost_transfers
        + sales_commissions            -- finance.finance_salaries, type = 'sales commissions'
        + adjustment
```

`adjustment` solo existe en meses cerrados (ver abajo). Vale `finance_salaries - (total_compensation_cost + capitalization + bonus_reversal + cost_transfer)`, así que **en un mes cerrado el hr_cost termina siendo lo pagado según `finance.finance_salaries`**, y en un mes abierto es el accrual de compensaciones.

**2. Pool a prorratear por departamento** (`hr_costs_to_prorate_monthly.hr_cost_to_prorate`):

| Departamento | Se le resta | Va a |
|---|---|---|
| CoR: 1 Operations, 2 Mixilo, 9 Habit | `delivery_cost` + `staffed_delivery_cost_forecast` de su BU (3, 2 y 5) | `cor_hr_cost_allocated` |
| Resto | su `overhead_cost` | `operating_hr_cost_allocated` |

El pool CoR es el **non-delivery cost**: costo de HR de los departamentos de delivery que no quedó imputado a horas delivery. Definición de negocio: HR cost allocated = costo total de HR − delivery cost. [CONFIRMADO POR AUGUSTO]

**3. Prorrateo:**

- **CoR:** por participación en el revenue dentro de la BU (`cor_revenue_share`). Si la BU no tiene revenue en el mes, partes iguales entre sus filas.
- **Operativo:** por participación en el revenue de toda la compañía (`operating_revenue_share`). Sin revenue, por costo.

**El pool cierra exacto.** En los 12 meses de 2026, la suma de `cor_hr_cost_allocated` en la MV es igual al pool CoR, con diferencia 0. Ningún pool de 2026 es negativo. **Se descartó la hipótesis de que la MV sobreasigna HR por no restar capitalización y bonus reversal**: ya vienen restados en `hr_costs_monthly`.

**Asimetría a tener en cuenta:** el `hr_cost` es por departamento del empleado, pero el delivery cost que se le resta es por BU de la cuenta. Una persona de Operations que imputa horas a una cuenta de Mixilo baja el pool de Mixilo, no el de Operations. Hoy no genera pools negativos, pero explica por qué el non-delivery cost de un departamento puede no coincidir con un cálculo por persona.

## Mes cerrado [CONFIRMADO POR AUGUSTO 2026-10-01]

**Un mes está cerrado cuando tiene `forecast = false` en `compensations.view_parameters`.** Es el mismo interruptor que activa el `adjustment` con los salarios pagados. Augusto lo marca al cargar los salarios pagados.

- La vista exige además filas en `finance.finance_salaries`, pero **esa tabla ya tiene montos para los meses futuros** [VERIFICADO 2026-10-01], así que en la práctica decide solo `forecast`.
- Al 2026-10-01: enero–agosto cerrados; septiembre en adelante con `forecast = true`.
- **No usar el criterio calendario** ("todo mes anterior al actual") para P&L ni gross profit: septiembre ya pasó y todavía no está cerrado.
- Algunas pantallas de compensaciones usan criterio calendario (ver `dominios-sin-verificar.md`). Es la regla de esa pantalla, no la definición de cierre.

## Otros objetos [VERIFICADO]

| Objeto | Tipo | Para qué |
|---|---|---|
| `time_tracking.delivery_cost_by_employee_monthly_mv` | MV | Detalle y desvíos por empleado, cuenta y mes |
| `time_tracking.company_delivery_utilization_employee_monthly_mv` | MV | Utilización por empleado y mes |
| `finance.expenses` | tabla | Gastos: `expense_id`, `period`, `account_id`, `type`, `amount` |
| `oas.control_center_user_account_access_mv` | MV | Alcance de cuentas por usuario: `work_email`, `account_id`, `is_admin` |

**Grants manuales [VERIFICADO 2026-09-28]:** `oas.control_center_access_grants` (`access_grant_id`, `employee_id`, `scope`, `account_id`, `client_id`, `area_id`, `country_id`, `comments`, `created_by/at`, `updated_by/at`) se administra desde BizOps Center · Access Management. `scope` ∈ `admin` (todo el Control Center), `account`, `client`, `portfolio` (area) o `country`. La MV combina esos grants con los roles de la cuenta (`access_sources`) y marca `is_admin`.

Hoy hay 15 grants: 9 `admin`, 4 `portfolio`, 1 `account`, 1 `country`. [VERIFICADO 2026-09-28]

Las queries del Control Center y del Staffing Center además recortan a **`business_unit_id IN (2, 3, 5)`**, que son las tres BU billable. Ops Retention Target usa solo la 3.

**Business units (`oas.business_units`)** [VERIFICADO 2026-09-28]

| id | business_unit | billable |
|---|---|---|
| 1 | Internal | no |
| 2 | Mixilo Services | sí |
| 3 | Professional Services | sí |
| 4 | Mixilo Product | no |
| 5 | HABIT Services | sí |
| 6 | HABIT Internal | no |

`control_center_user_account_access_mv` recorta cuentas en la mayoría de las consultas de la app, pero **no en el reporte de utilización**. Es alcance implementado consulta por consulta, no una política de permisos de la base.

## Clasificación de horas y costo [SQL APP — medidas DAX]

Cruza dos flags, no uno:

| Cuenta billable | Empleado CoR | Categoría |
|---|---|---|
| sí | sí | delivery |
| no | sí | non-delivery |
| sí | no | overhead |
| no | no | internal |

Usa `business_units[account_billable]` y `dedications[employee_cost_of_revenue]`, **no** el tag `employees[billable]`.

## Utilización: son dos medidas distintas [SQL APP]

- **Utilización delivery** = horas delivery / (horas delivery + horas non-delivery).
- **`kpis_utilization`** = horas delivery / todas las horas imputadas.

No son intercambiables y aparecen las dos en el Power BI. Con denominador cero devuelven `null`, no cero.

**La que se reporta hacia afuera es `kpis_utilization`.** [CONFIRMADO POR AUGUSTO 2026-10-01] Si piden "la utilización" sin aclarar, usar esa. La utilización delivery es de uso interno.

Desvío de costo = `delivery_cost - staffing_delivery_cost`; desvío relativo = esa diferencia / `ABS(staffing_delivery_cost)`, `NULL` si el plan es cero. **Es fracción, no porcentaje.**

## Targets y umbrales

| Métrica | Valor | Estado |
|---|---|---|
| Gross margin (`gross_profit_margin`) | 41% | **Target de la compañía** [CONFIRMADO POR AUGUSTO 2026-10-01] |
| Delivery gross margin | 60% | **Target de la compañía** [CONFIRMADO POR AUGUSTO 2026-10-01] |
| Utilización | 80% | **Solo semáforo de la app.** No reportarlo como objetivo. |

Los tres están hardcodeados en el JavaScript del Control Center para pintar semáforos. Un target se compara contra el margen recalculado sobre los totales, nunca contra un promedio de márgenes.

## Riesgos

- Confundir `delivery_gross_profit` con `gross_profit`.
- Sumar todo el staffing al costo reportado en vez de solo `staffed_delivery_cost_forecast`.
- Mezclar utilización delivery con `kpis_utilization`, o reportar la delivery hacia afuera.
- Tratar como cerrado un mes con `forecast = true` en `view_parameters`.
- Comparar un P&L del mes en curso entre dos días distintos: el staffed forecast cambia a diario.
- Buscar una columna `period` en `mv_project_metrics_monthly`: es `month_start`.
- Presentar una diferencia entre pantallas como error de datos sin antes igualar alcance, período y fórmula.
- Duplicar agregados financieros al unirlos con la tabla de personas.
