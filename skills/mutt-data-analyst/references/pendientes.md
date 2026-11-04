# Pendientes

## A) Se resuelven leyendo la base — no preguntar, ejecutar

Estas quedan pendientes solo por tiempo. La forma de resolverlas es
`pg_get_viewdef('schema.objeto'::regclass, true)`.

- Definiciones completas de las vistas de compensaciones: qué componentes
  integran `total_compensation_cost`.

**Resueltos 2026-11-04:** `delivery_cost_by_employee_monthly_mv` y los shares de
prorrateo (ver `control-center-pnl.md`), `view_headcount_plan` y
`parameters_info` (ver `dominios-sin-verificar.md`).

**Resueltos 2026-10-06:** `_weighted` de `deals_assignments_metrics` (ver
`staffing.md`), `company_delivery_utilization_employee_monthly_mv` (no
precalcula utilización, ver `control-center-pnl.md`), insumos de `mv_master` y
`finance.view_salary_cost` (ver `time-tracking.md`).

- ~~Reconciliación del pool de HR en la MV~~ — **resuelto 2026-10-01**: cierra
  exacto, ver `control-center-pnl.md`.

## B) Solo las puede contestar Augusto

Decisiones de negocio o conocimiento que no está en la base.

### Definiciones en disputa

- **Bench.** Hay tres definiciones conviviendo: umbral 70 en Staffing Center,
  0,70 con población distinta en el Power BI, y el bench de recruiting del
  scorecard. ¿Cuál es la oficial, o cada una tiene su uso legítimo?
- **El factor 2,5 de `target_revenue`** está hardcodeado en
  `view_project_metrics_monthly`. ¿De dónde sale y cada cuánto se revisa?

### Vigencia

- ¿Sigue vigente la equivalencia FEMSA/KOF y el recorte a Portfolio 1–5 en la
  pantalla de alineación?
- ¿Qué versión del Power BI y de las apps es la de referencia cuando dos
  fórmulas difieren?
- ¿Las apps (Revenue Commit Control y el Control Center) ya leen el commit desde
  `simulation_revenue.revenue_plans`, o todavía desde `revenue_commit_q3`?
- `delivery_cost_by_employee_monthly_mv` todavía deja los deals HS en el país de
  la cuenta genérica (Argentina). ¿Se alinea con `deals_resolved`, como la vista
  del P&L?
- **Fuera de la skill por decisión de Augusto (2026-10-30), hasta que estén
  validados:** el contenido de los targets del Scorecard
  (`scorecard.kpi_targets`, `manual_targets`) y el tiering de cuentas
  (`oas.account_tiers` y tablas relacionadas). No documentarlos ni usarlos.

**Resuelta 2026-11-04:** la vista del P&L ya asigna país y región de los deals
HS con `deals_resolved`; revenue y márgenes por región cuadran.

**Resuelta 2026-10-30:** el commit de Q4 existe (planes de
`simulation_revenue`); los snapshots corren los jueves.

**Resueltas 2026-10-06:** los deals con stage sin mapear quedan fuera a
propósito (etapas muy tempranas); criterio de país del P&L by Geo; definición de
utilización delivery billable.

### Semántica

- Qué significan los niveles 1–3 de skills (`level_score`) y cuánto dura la
  vigencia de una respuesta.
- Qué significan `orientation_score` (`exceeds` / `meets` / `partially_meets`) y
  `promotion_readiness` (`not_ready` / `ready_soon` / `ready_now`), y si
  committee es la evaluación final. Los valores ya están verificados; falta la
  definición de negocio.
- Qué define cada color de `people.status` y quién resuelve las acciones.
- Qué son en el negocio la capitalización (`employee_salary_impact_recovery`) y
  el bonus reversal (`employee_bonus_recovery`), y qué representa un cost
  transfer. **El cálculo ya está verificado**: entran a `hr_costs_monthly` con
  signo negativo los dos primeros (ver `control-center-pnl.md`); falta la
  definición de negocio.
- Qué son los montos de `finance.finance_salaries` en meses con
  `forecast = true`: ¿proyección, budget o carga anticipada?
- Qué expande la sigla RDG y quién opera aprobación y pago.

### Responsables

Casi todos los dominios identifican roles (`account_lead`, `delivery_lead`,
`director`, `hrbp`, `approver_id`, `authorizer_id`) pero ninguna consulta
demuestra quién decide qué. Si querés que la skill sepa a quién mandar una
pregunta, hay que escribirlo a mano.

## C) Deuda de la skill

- `references/metrics.md` y `references/entities.md` vienen de la versión
  anterior y todavía cubren solo revenue. Conviene revisarlos ahora que hay más
  dominios.
- No hay archivo de golden questions: diez preguntas con su número correcto,
  para correr después de cada cambio grande y detectar regresiones.
- Los conteos de filas están fechados pero se vencen. Al actualizar la skill,
  reconsultarlos o borrarlos.
- **Modelo nuevo de posiciones (schema `staffing`)**, en construcción. Cuando
  reemplace a `oas.deals_assignments`, reescribir `staffing.md`,
  `deals_assignments_metrics` y `scorecard.mv_staffing_weekly`.
- **Rediseño del modelo de compensaciones** (en curso, nov 2026): la idea es un
  SSOT de salarios pagados que cargue Finance y que el forecast se alinee con
  eso. Cuando se implemente, revisar `finance.view_salary_cost`,
  `paid_and_payroll_salaries`, el cierre de mes (`view_parameters`) y
  `time-tracking.md` § insumos de `mv_master`.
- `view_headcount_plan` tiene 2026 fijo: en 2027 no va a generar meses (ni el
  cálculo de Operations) hasta que se actualice.
- Falta un mapa de qué objetos lee y escribe cada app de Appsmith. Necesita los
  exports o los repos.
