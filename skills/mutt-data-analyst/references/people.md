# People: headcount, turnover, exits, eNPS, 1:1s y organigrama

Fuentes vigentes: `bamboo` (directorio e historiales) y `people` (seguimiento).
Las definiciones salen de dos apps que ya reemplazaron al Power BI "People":

- **People Analytics** (People Center, página Analytics, en `master` desde
  2026-11-06). Recalcula todo en la widget a partir de las filas.
- **MBR Report**, página People (2026-10-20). Réplica de las slides People del
  QBR Q3 2026, validada contra el deck de septiembre 2026.

Recruiting (`lever`) está en `lever.md`. Performance reviews y skills están en
`development.md`. Voice of Mutters y lo que escribe People Management siguen en
`dominios-sin-verificar.md`.

---

## Quién está activo [CONFIRMADO POR AUGUSTO + VERIFICADO 2026-11-06]

- Activo en la fecha `d`:
  `hire_date <= d AND (termination_date IS NULL OR termination_date >= d)`.
  **`termination_date` es el último día trabajado**, así que ese día la persona
  cuenta.
- **`bamboo.employees_joined` incluye ingresos futuros.** Al 2026-11-06,
  `status = 'Active'` da 210 y los activos hoy son 203: la diferencia son 7
  personas con `hire_date` futura. Para cualquier headcount, filtrar por fechas,
  no por `status`.
- Los ingresos futuros sirven para "Upcoming Mutters": ingresos con `hire_date`
  en el mes siguiente al elegido [SQL APP, MBR].
- **Recontratados:** cuenta solo el período actual de `employees_joined` (una
  fila por persona). El período anterior no aparece como baja ni como headcount.

## Headcount [SQL APP, validado contra el deck de septiembre 2026]

| Variante | Definición | Uso |
|---|---|---|
| **Promedio** (default) | promedio, sobre los días del período, de los Mutters activos cada día | Turnover, headcount promedio de los decks, revenue por Mutter |
| **End / cierre** | activos el último día del mes (hoy, si el mes está en curso) | "Headcount de cierre" del deck, organigrama |
| **Start** | activos el día 1 | Opening del waterfall |
| **Mid** | activos el día 15 | People Analytics |
| **Today** | activos hoy | Tortas de People Analytics |

- En períodos de varios meses (People Analytics: Q, Y): Start = primer día del
  período, End = último día, Mid = promedio de los días 15. Un día que todavía
  no llegó no da valor.
- **Waterfall del mes:** la app presenta Opening (día 1) + hires − exits =
  Closing. Para reconciliar con las fechas inclusivas de activos, contar altas
  después del día 1 y hasta el cierre, y bajas desde el día 1 pero anteriores
  al cierre. Un alta del día 1 ya está en Opening; una baja del último día
  todavía está en Closing. El deck calculaba el inicio hacia atrás desde el
  cierre: Aug 194 → Sep 192.
- **Delivery vs non-delivery:** departamento con
  `oas.departments.cost_of_revenue = true`, unido **por nombre**
  (`lower(trim(department))`).
- **Ops billable:** `department = 'Operations' AND billable`.
- Validado contra el deck de septiembre 2026: headcount promedio y delivery mix
  (Oct 25 164 = 132 + 32 … Sep 26 149 delivery). Agosto 2026: promedio 192,9
  (deck 193).

```sql
WITH days AS (
  SELECT gs::date AS d, date_trunc('month', gs)::date AS m
  FROM generate_series(date '2026-01-01', current_date, interval '1 day') gs
)
SELECT to_char(m, 'YYYY-MM') AS month,
       round(avg(n), 2) AS headcount_avg,
       (array_agg(n ORDER BY d DESC))[1] AS headcount_eom
FROM (
  SELECT d.m, d.d, count(e.employee_id) AS n
  FROM days d
  LEFT JOIN bamboo.employees_joined e
    ON d.d >= e.hire_date AND (e.termination_date IS NULL OR d.d <= e.termination_date)
  GROUP BY 1, 2
) x
GROUP BY m ORDER BY m;
```

## Departamento y step: los actuales, no el historial [SQL APP]

- **Cortes por departamento o step usan el departamento y el step actuales** de
  `employees_joined`, aplicados hacia atrás. Así lo hacen el People Headcount
  Dashboard, MBR y People Analytics. Con el historial de `job_information` /
  `career_path` los números no coinciden con ningún tablero.
- "Headcount change" por departamento y step (MBR): cierre del mes elegido −
  cierre del anterior. El acumulado es contra el cierre de diciembre del año
  anterior. Incluye promociones y cambios de área.
- **Agrupado de departamentos del Power BI** (`department_group` en People
  Analytics):

| `department` | Grupo |
|---|---|
| `Founder`, `G&A` | G&A |
| `Mixilo`, `Mixilo - Tech` | Mixilo |
| `Bench`, `External Projects`, `Operations`, `Operations - Data Architecture`, `Operations - Data Engineering & Analytics`, `Operations - ML services` | Operations |
| `Sales & Marketing`, `Sales & Marketing - Sales` | S&M |
| `Internal Projects`, `Tech` | Tech |
| NULL | (Blank) |

- **Área** (`division`): `Data Architecture` → DA,
  `Data Engineering & Analytics` → DEA, `Media & GenAI` → MAGA,
  `Machine Learning Services` → MLS. Los valores `IC1`–`IC5`, `M1` y `None` son
  steps cargados por error en la división: van como None.
- El historial (`bamboo.job_information`) sí sirve para el organigrama en el
  tiempo (ver § Organigrama).

## Turnover [SQL APP, validado contra el deck de septiembre 2026]

- **Turnover del mes** = bajas del mes / headcount promedio del mes.
- **L12M** = bajas de los 12 meses / promedio de los 12 headcounts promedio
  mensuales. No es la suma de los 12 turnovers.
- **Bajas**: filas de `employees_joined` con `termination_date` en el período y
  `<= current_date`. Columnas para cortar:
  - `termination_type`: `'Resignation (Voluntary)'` o
    `'Termination (Involuntary)'`.
  - `regrettable`: `'Regrettable'`, `'Non-Regrettable'` o NULL.
  - `contract_type`: `RDD`, `Contractor` o `Subcontractor`.
- Validado exacto contra septiembre 2026: L12M voluntario 36 / 20,0%, su split
  regrettable / non-regrettable mes a mes, y regrettable L12M 21 (11,7%; el deck
  redondea a 12%).
- Las tarjetas de turnover por año, L12M y L3M de People Analytics ignoran el
  filtro Date, como el Power BI.
- **Antigüedad y edad de una baja: a la fecha de baja**, no a hoy. El Power BI
  las calculaba a hoy.
- **Turnover Comparison** (People Analytics): pivots de hires y bajas por mes y
  departamento, por step, y **neto por step** (hires − bajas).

## Exits y exit interviews [SQL APP]

- **Motivos de salida** = `termination_reason` de Bamboo (voluntarias e
  involuntarias). La entrevista tiene su propio `termination_reason`; si difiere
  del de Bamboo, se muestra aparte, pero el motivo oficial es el de Bamboo.
- `people.view_exit_interviews` se une a la baja por `employee_id`. Si hay
  varias, la última por `created_date`.
- **Salary difference** (MBR): entrevistas **por fecha de entrevista** en los
  mismos 12 meses, sin `N/A`. Así da exacto el deck: 9 / 9 / 7 / 3.
- **Completitud de exit interviews**: desde la fecha de la primera entrevista
  cargada. Antes de esa fecha no se hacían, así que no cuentan como faltantes.
- Las respuestas de People, Technical y eNPS de la entrevista son **semáforos**.
  eNPS Recommend / Return = % Green − % Red.
- Para geografía, usar `country`, no `location`.

## eNPS del status quincenal (Muttito)

[SQL APP, validado contra las 19 encuestas de 2026]

`people.view_status`: un form por Mutter y ciclo quincenal. `value` = semáforo
del Mutter (`Green` / `Yellow` / `Red`). `supervisor_status_value` = semáforo
del lead.

- **eNPS** = `100.0 * (n_green - n_red) / NULLIF(n_respuestas, 0)`, donde
  `n_respuestas` cuenta `value` en Green / Yellow / Red. Rango −100 a 100;
  no multiplicar por 100 otra vez. Es el "NPS Status" del Power BI, no una
  encuesta 0–10.
- **Ciclo** = `created_date`. Las tarjetas de MBR muestran la
  **última encuesta del período**: el deck dice "eNPS Average" pero muestra la
  última.
- **"Excluding <3 months"** =
  `hire_date < date_trunc('month', created_date) - interval '3 months'`. Así se
  reproducen las 19 encuestas de 2026 del reporte de eNPS.
- **% Response** = forms enviados ÷ forms (del Mutter, no del lead). Las
  acciones (`action_need`, `action`, `resolved`) también son del form.
- **Semáforo del lead**: existe desde el ciclo del **2026-06-25** [VERIFICADO
  2026-11-06]. Antes de esa fecha, `supervisor_status_value` está vacío: no es
  falta de respuesta.
- Rankings por Mutter o por lead (People Analytics): mínimo 5 forms enviados. Un
  eNPS 0 cuenta como 0 (el Power BI lo dejaba en blanco).
- `people.status` no deja borrar un status ya enviado (trigger).

## Pulse Survey viejo [SQL APP]

`people.pulse_survey`, `pulse_survey_questions`, `pulse_survey_answers` (score
0–10) y `pulse_survey_comments`. Es la historia anterior a Voice of Mutters: no
se carga más.

- eNPS del Pulse: solo la pregunta "recommend Mutt", con la escala NPS clásica
  (9–10 promotor, 0–6 detractor, **el 0 incluido**).
- Filtra por `period`, no por fecha.
- No usar `people.pulse_survey_backup_20260603`.

## 1:1s [SQL APP, People Analytics 2026-11-05]

`people.view_one_to_one` (incluye ex Mutters, para no perder cobertura
histórica).

- **`supervisor_id` de la 1:1 = quién la hizo.** Casi siempre el líder: en 2026
  el HRBP hizo 3 de 180.
- **Fecha** = `COALESCE(meeting_date, created_date)`: el form se puede llenar
  días después.
- **Cobertura** = Mutters activos en el período con al menos una 1:1 ÷ Mutters
  activos en el período. El Power BI contaba todo el historial en el
  denominador.
- **Coverage by leader** = reportes directos actuales
  (`employees_joined.supervisor_id`) con 1:1 ÷ reportes directos.
- **HRBP** = `people.view_hrbp`: una fila por activo hoy (203 al 2026-11-06),
  tomada de la cuenta actual del Mutter. Las bajas no tienen HRBP. Los activos
  sin HRBP son internos ("No HRBP (internal)").
- Los semáforos de la 1:1 son `semaphore_assignment_satisfaction` y
  `semaphore_client_satisfaction`.
- `GetOneToOneHistory` de People Management incluye reuniones donde la persona
  es empleado **o** supervisor.

## People Talks

`people.talks`: `owner_id`, `supervisor_id`, `reason` y semáforos de assignment,
team, professional development y compensation, cada uno con su texto.

## Organigrama [VERIFICADO 2026-11-06]

- **Hoy:** `bamboo.employees_joined.supervisor_id`, filtrando activos por fecha.
  Al 2026-11-05: 203 activos, 57 managers y 7 capas. El schema `orgchart` está
  desactualizado.
- **En el tiempo:** `bamboo.job_information`, 1.581 filas al 2026-11-06. Llevado
  a una fila por persona y fecha de cambio, desde 2018, quedan 1.473:
  - `reporting_to` viene **por nombre**. Se resuelve contra
    `employees_joined.employee` y hoy matchean todos.
  - Departamento: `'Operations - ML services'` se normaliza a `Operations`.
  - División: NULL cuando la fila trae un step en ese campo.
  - Jefe a una fecha = último cambio de `job_information` hasta esa fecha. Si
    ese jefe ya no está activo, la persona cuelga del jefe de su jefe.
  - La última fila de cada activo coincide con `supervisor_id` y el departamento
    de hoy: 0 diferencias.
- Validación: el organigrama de septiembre 2026 da 191 al cierre, igual que
  People.
- **Un organigrama abierto a toda la empresa lleva solo campos de directorio**
  (nombre, foto, rol, departamento, división, país, ingreso). Sin compensación,
  step, billable ni asignaciones.

## Datos sensibles

- `bamboo.compensation_scheme` (`gross_salary`, `currency`, `usd_20`, bonos): no
  exponerlo en salidas de alcance amplio.
- Voice of Mutters es anónima por diseño: no cruzar `vom_participations` con
  `vom_responses` (ver `dominios-sin-verificar.md`).
- Motivos de baja, regrettable y exit interviews son de uso interno de People y
  de leadership.

## Errores frecuentes

- **Contar activos con `status = 'Active'`**: incluye los ingresos futuros.
- **Cortar por departamento con el historial de `job_information`**: no coincide
  con los tableros, que usan el departamento actual.
- **Calcular el L12M como suma o promedio de turnovers mensuales.**
- **Usar headcount de cierre para el turnover**: el denominador es el promedio
  diario.
- **Tomar el motivo de la exit interview como motivo oficial**: el oficial es el
  de Bamboo.
- **Leer el eNPS del lead antes del 2026-06-25**: el campo no existía.
- **Calcular la antigüedad de una baja a hoy.**
- **Sumar headcounts de áreas de `employee_area_allocations`**: una persona
  puede estar en varias.
