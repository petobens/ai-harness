# Dedicaciones y time tracking

Schema `time_tracking`. Responde dónde se dedicó la capacidad, cuánto falta
reportar y qué costo se imputa a cada proyecto o deal.

## Objetos [VERIFICADO 2026-09]

| Objeto | Tipo | Para qué |
|---|---|---|
| `time_tracking.forms` | tabla | Formularios: `employee_id`, `approver_id`, fechas, estado |
| `time_tracking.dedications` | tabla | Líneas: `dedication_id`, `form_id`, `project_id`, `deal_id`, `dedication` |
| `time_tracking.form_approvals` | tabla | Resoluciones del formulario |
| `time_tracking.dedications_rejected` | tabla | Copia de líneas al rechazar |
| `time_tracking.autosubmit_rules` | tabla | Autoenvíos: `employee_id`, vigencia, `lines_json` |
| `time_tracking.mv_master` | MV | **Base de todo el cálculo de costo.** Trae el salario, el standard cost y los días/horas de cada persona |
| `time_tracking.view_master_final` | vista | **La que hay que usar** para horas y costo imputados |
| `time_tracking.view_forms` / `view_dedications` | vistas | Workflow |
| `time_tracking.bizops_forms_history` / `bizops_form_dedications` | vistas | Pantallas de BizOps |

## Fórmulas reales de `view_master_final`

[VERIFICADO — leídas de la definición de la vista]

Esto es lo que antes figuraba como desconocido. Las tres columnas que consume el
Power BI se calculan así:

```text
effective_working_hours = COALESCE(NULLIF(working_hours, 0), 8)
base_cost               = COALESCE(salary_cost, standard_cost)
used_standard_cost      = (salary_cost IS NULL)

assigned_hours          = dedication * working_hours / 100

assigned_cost           = base_cost * dedication / (divisor * 100)
assigned_standard_rate  = standard_rate / divisor / 8 * effective_working_hours * dedication / 100
```

**El `divisor` cambia según el mes:**

- `weekly_days` en un mes normal.
- `worked_days` (días distintos efectivamente reportados ese mes) cuando el mes
  es el de ingreso o el de egreso de la persona. Ese es el flag
  `full_employee = false`.

Consecuencias:

- **No hay supuesto de 8 horas ni de 20 días.** Sale de `working_hours` y
  `weekly_days` de cada persona. El 8 que aparece en `standard_rate` es el
  divisor de una jornada estándar para prorratear la tarifa, no una jornada
  asumida.
- **El costo cae a standard cost cuando no hay salario cargado.**
  `used_standard_cost = true` marca esas filas. Si vas a comparar costo contra
  payroll, filtralas o aclaralo.
- **`dedication` viene en 0–100** en esta vista. El Power BI la divide por 100
  al cargarla.

## De dónde salen los insumos de `mv_master` [VERIFICADO 2026-10-06]

| Columna | Origen |
|---|---|
| `salary_cost` | Último `finance.view_salary_cost` con mes ≤ al mes del día. **Arrastra el último salario conocido** |
| `has_salary_cost` | Hay salario cargado para ese mes exacto |
| `standard_rate`, `standard_cost` | Step vigente en `bamboo.career_path` → `oas_views.steps` |
| `department`, `employee_department_id`, `employee_cost_of_revenue` | Último `bamboo.view_job_information` del mes → `oas.departments`, **unido por nombre** (`lower(trim())`) |
| `working_hours` | Último `bamboo.compensation_scheme`; 8 si es 0 o NULL |
| `weekly_days` | Días hábiles del mes |

**`finance.view_salary_cost`:** hasta 2025 sale de `finance.salary_costs`. Desde
2026 es `total_compensation_cost` de `compensations.paid_and_payroll_salaries`,
hasta el **mes calendario anterior** y excluyendo `employee_id >= 900000` (los
planificados de `payroll_needs`). Usa criterio calendario, no el flag
`forecast`.

Consecuencias:

- **El mes en curso se costea con el salario del mes anterior**, y
  `used_standard_cost` no lo marca: solo es `true` cuando la persona no tiene
  ningún salario previo. Para distinguir el arrastre, mirar
  `has_salary_cost = false`.
- **El join de departamento por nombre es frágil.** Hoy no deja horas sin
  categoría, pero si cambia el nombre de un departamento en Bamboo,
  `employee_cost_of_revenue` queda NULL y esas horas salen de las cuatro
  categorías de delivery.

## Qué deals puede reportar cada uno en Muttito

[SQL APP Muttito `GetTimeDeals`, 2026-11-05]

Un Mutter puede cargar horas en un deal (todavía sin proyecto) si se cumple
alguna de estas:

1. Tiene una asignación en ese deal (`oas_views.deals_assignments`).
2. Puede reportar **todos** los deals abiertos: departamento `Sales%`, step
   M2–M6 o E1–E3, división `BizOps`, o PMO (Augusto Peña, Giuliano Faggiani).
3. Es del equipo de HABIT (departamento `Habit` o la lista de Mati Vila en la
   query): puede reportar **solo deals de HABIT Services**.

- Por eso hay horas de no asignados en deals de HABIT, de BizOps y de managers.
  **No son un error de carga.**
- El selector de deals se parte por business unit. Los deals (HS) muestran el
  logo de su compañía de HubSpot.

## Reglas del workflow [SQL APP]

- El envío exige `SUM(dedication) = 100` por formulario, y exactamente uno de
  `project_id` o `deal_id` por línea. La suma 100 la impone además un trigger de
  `time_tracking.dedications` en insert, update y delete [VERIFICADO
  2026-10-30].
- La validación de Muttito admite hasta 20 líneas y múltiplos de 5, y permite
  cero en una línea; la vía administrativa exige valores positivos. Son dos
  caminos con validaciones distintas.
- **Rechazar** copia las líneas a `dedications_rejected`, borra las vigentes,
  agrega resolución `Rejected`, limpia `submitted_date` y extiende
  `expired_date` 7 días. Analizar solo las líneas vigentes no reconstruye los
  rechazos.
- La última resolución se toma por `resolved_at DESC, approval_id DESC`. Un join
  a todas las aprobaciones multiplica el formulario.
- El dashboard de BizOps clasifica `Approved` por descarte, después de separar
  pendientes de envío y de aprobación. No prueba una aprobación explícita
  registrada.

## Métricas [SQL APP]

| Métrica | Fórmula |
|---|---|
| Tasa de respuesta | formularios `Submitted` / total de formularios |
| Puntualidad | `On Time` / (`On Time` + `Delayed`) — **no** sobre el total |
| Horas imputadas | `SUM(assigned_hours)` |
| Costo imputado | `SUM(assigned_cost)` |

Aprobación (`Pending` / `Approved` / `Rejected`) es un eje distinto de envío y
puntualidad. No mezclarlos en el mismo denominador.

## Riesgos

- Tomar enviado como aprobado.
- Contar un formulario varias veces por sus líneas o sus resoluciones.
- Sumar `dedication` entre días como si fueran porcentajes acumulables.
- Comparar costo imputado contra payroll sin separar las filas con
  `used_standard_cost = true`.
