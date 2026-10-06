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

## Reglas del workflow [SQL APP]

- El envío exige `SUM(dedication) = 100` por formulario, y exactamente uno de
  `project_id` o `deal_id` por línea.
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
