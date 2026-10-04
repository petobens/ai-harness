# Dominios con nombres verificados y fórmulas sin verificar

Material extraído del SQL de las apps y del Power BI. **Todos los nombres de objetos de este archivo fueron chequeados contra la base y existen** (verificado 2026-09). Las fórmulas y reglas **no** fueron verificadas contra la definición de las vistas: usarlas para orientarse, no para un número que va a una presentacion sin confirmarlas antes.

---

## Compensaciones y payroll

Objetos: `compensations.paid_and_payroll_salaries` (MV, serie combinada), `payroll_metrics`, `payroll_all`, `payroll_needs`, `parameters`, `view_parameters` (vistas), y los inputs `paid_salaries_rdd`, `paid_salaries_contractors`, `paid_salaries_subcontractors` (tablas). RDD se vincula a `bamboo.employees` por `cuil`; los otros dos traen `employee_id`. La comparacion une por `employee_id` y `period`.

- **Desvio de costo:** pagado - forecast. **Porcentual:** `100 * (pagado - forecast) / ABS(forecast)`, NULL si forecast es cero. Solo para periodos anteriores al mes actual.
- **Matched:** diferencia absoluta <= `GREATEST(1, ABS(forecast) * 0.01)`. Usa FULL OUTER JOIN, asi que distingue `Paid only`, `Forecast only`, `Variance` y `Forecast`.
- El criterio de periodo cerrado es **puramente calendario**. No prueba cierre contable.
- **Este dominio si tiene moneda propia:** `currency`, `official_usd`, parametros `_ars` y `_usd`. La regla USD de revenue no aplica aca.
- `payroll_needs` fabrica IDs con `990000 + ROW_NUMBER()` y estado `Planned`. No son empleados reales.
- No hay imputacion directa de payroll a deal o cuenta: la conexion pasa por dedicaciones o asignaciones.

**Objetos que usa Compensation Center [VERIFICADO 2026-09-28] (existencia; fórmulas sin leer):** `compensations.headcount_plan` / `view_headcount_plan` (plan de headcount, con upsert y delete desde Parameters), `salary_band`, `payroll_restriction`, `contractor_special_fees`, `employee_extra_compensations`, `working_hour_adjustments`, `parameters_info`, y `finance.view_salary_cost` (vista con `employee_id`, `month`, `salary_cost`: salario mensual por empleado, usado en Dedication Control). Filas aproximadas: `headcount_plan` 72, `salary_band` 26, `contractor_special_fees` 2, `payroll_restriction` 1, `employee_extra_compensations` 0.

**Dedication Control** compara `finance.view_salary_cost` contra el costo imputado, uniendo dos fuentes de dedicaciones: `time_tracking.view_master_final` (`'Current'`) y **`time_tracking_old.view_master_final` (`'Legacy'`)**. Solo meses cerrados (anteriores al mes actual) y separando `used_standard_cost`. [VERIFICADO 2026-09-28] `time_tracking_old` cubre **2022-01-03 a 2024-12-31** (112.648 filas) y `time_tracking` arranca el **2025-01-01**. Para historia anterior a 2025, la fuente es `time_tracking_old` (`view_master_final`, `mv_master`, `dedications_daily`).

## Time tracking: iniciativas internas

[VERIFICADO 2026-09-28] `time_tracking.internal_initiatives` tiene una sola columna, `form_id` (~140 filas): es la lista de formularios marcados como iniciativa interna. Muttito la escribe con el flag `internal_initiatives` al enviar. Las líneas del formulario siguen teniendo `project_id` o `deal_id`.

## P&L: distribucion de costos a areas

Objetos: `compensations.employee_area_allocations` (tabla), `employee_cost_transfers`, `employee_salary_impact_recovery`, `employee_bonus_recovery` (vistas), `employee_salary_impact` (tabla), `oas.areas`, y para conciliar `finance.hr_costs_monthly` (vista), `finance.finance_salaries` (tabla).

- **`allocation_pct` suma 1,00 por empleado y periodo. [VERIFICADO: 102 pares, cero invalidos.]** Sin asignacion explicita se toma 1,00 al area original.
- **Costo distribuido:** cada componente salarial x `allocation_pct`, redondeado a dos decimales antes de agregar.
- **Costo neto P&L:** distribuido - `salary_impact_recovery` - `bonus_recovery`.
- **Costo de sistema para Finance:** `total_compensation_cost + capitalization + bonus_reversal + cost_transfer`.
- Las transferencias ya se usan para reconstruir el cambio de imputacion. Sumarlas otra vez al distribuido duplica el movimiento.
- El headcount por area usa `COUNT(DISTINCT employee_id)` y **puede repetir una persona entre areas**. No sumar headcounts de areas.
- Distribucion a areas no es lo mismo que imputacion por dedicacion a un proyecto.

## Clientes, cuentas y proyectos

Escritura en `oas.clients`, `oas.accounts`, `oas.projects`; lectura en `oas_views.clients`, `accounts_joined`, `projects_joined`.

La cuenta tiene `business_unit_id`, `area_id` y responsables: `account_lead_id`, `delivery_lead_id`, `project_administrator_id`, `executive_sponsor_id`, `sales_lead_id`, `hrbp_id`. El proyecto tiene `phase_id`, `folder_id`, `slack_channel_id`.

Las altas ejecutan `set_config('app.user_email', ...)`, lo que indica contexto de usuario en las escrituras. Que tabla guarda esa auditoria no esta identificado.

## People: directorio y seguimiento

Lectura central `bamboo.employees_joined`; historiales en `bamboo.job_information`, `employment_status`, `compensation_scheme`, `development`, `view_career_path`. Seguimiento en `people.status` / `view_status`, `one_to_one` / `view_one_to_one`, `talks` / `view_talks`, `view_exit_interviews`, `hiring_checkup`.

- **Headcount del PBIX:** promedio de la cantidad diaria de empleados distintos. **No es dotacion al cierre.**
- **Turnover:** bajas / headcount promedio. Altas cuenta empleados distintos; bajas cuenta filas.
- **NPS Status:** `(Green - Red) / formularios enviados x 100`. Es el nombre interno de esa medida; no es una encuesta 0-10.
- `hires_terminations` y `employees_per_day` son tablas calculadas DAX, no objetos de PostgreSQL.
- `GetOneToOneHistory` incluye reuniones donde la persona es empleado **o** supervisor.
- Los checkups distinguen 3m y 6m con campos distintos en cada uno.

**Objetos que usa People Center [SQL APP, 2026-09-28]:**
- **People Management** lee `people.view_status`, `view_one_to_one`, `view_talks`, `view_exit_interviews` y `view_hrbp`, más `oas_views.accounts_joined` y `projects_joined`.
- **People Management** escribe en `people.status` (update), `people.talks` y `people.exit_interviews` (insert, update y delete), y el HRBP de la cuenta en `oas.accounts.hrbp_id`.
- **Mutters Directory** lee `bamboo.employees_joined`, `job_information`, `employment_status`, `compensation_scheme`, `view_career_path` y `development.*` (ver `references/development.md`).
- **La lista de cuentas del HRBP excluye `client_id` 26 y 44 [VERIFICADO].** No son clientes reales: son los contenedores "Target Leads" y "Hubspot Deals". Excluirlos también en cualquier conteo de cuentas o clientes.
- `bamboo.compensation_scheme` tiene salario bruto (`gross_salary`, `currency`, `usd_20`, bonos). Es dato sensible: no exponerlo en salidas de alcance amplio.

## Development y performance reviews

Movido a `references/development.md`, verificado contra la base el 2026-09-28.

## ClickUp: salud de delivery

`oas.clickup_cards`: `task_id`, `project_id`, `folder_id`, `list_id`, `client_status`, `client_complaints`, `archived`, `url`.

- **Client Complaints:** tareas con `client_complaints = 'Yes'`. **Red:** `Fearful`. **Amarillas:** `Regular expectations` o `Doubtful`. **Verdes:** `Optimistic` o `Completely on board`.
- Todas cuentan `DISTINCTCOUNT(task_id)`: **son tarjetas, no clientes.**
- Las medidas base no excluyen `archived`. Que fecha gobierna la serie no esta definido.

## RDG: gastos y autorizacion

`people.rdg` / `people.view_rdg`: `rdg_id`, `employee_id`, `invoice_date`, `concept`, `amount`, `currency_id`, `receipt_link`, `authorizer_id`. Catalogo de monedas en `vuriltek.monedas`: es lo único vigente del schema `vuriltek`, porque `view_rdg` depende de él.

- `view_rdg` distingue `authorized`, `approved` y `paid`. **Autorizado no es pagado.** Falta de resolucion no es denegacion.
- El alta no tiene `deal_id`, `project_id` ni `account_id`. No hay imputacion a cliente demostrada.
- Sumar montos por moneda por separado hasta tener una conversion validada.

## Seguridad de equipos (solo Muttito)

**Fuera del alcance de análisis.** Estos objetos los usa únicamente la app Muttito; no usarlos para reportes ni KPIs salvo pedido explícito. `tech` es un schema del equipo tech.

`tech.employees` (vista), `security_tracking.wazuh_agents`, `security_tracking.observations`, vinculados por `work_email` / `user_email`.

- Indicadores: `dns_status`, `antimalware_status`, `encryption_status`, todos contra `'passed'`.
- Toma un agente por persona con `last_keep_alive DESC LIMIT 1`. **Sin dato no es incumplimiento**, y un agente no es el inventario completo.

## Scorecard financiero manual

`oas.scorecard_manual`. Las medidas `Cash to Expenses`, `Delayed Invoicing Over 30 Days` y `Overdue Payments` son **promedios de valores cargados a mano**, no calculos sobre facturas. Un promedio de porcentajes reportados no equivale al porcentaje recalculado sobre importes. No hay una fuente vigente de caja, facturas o cobranzas para reconciliarlos. `sas` (`view_facturas_final`, `view_cobros`) y `vuriltek.cashflow` son del billing viejo, que ya está muerto: no usarlos.
