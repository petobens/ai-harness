# Pendientes

## A) Se resuelven leyendo la base — no preguntar, ejecutar

Estas quedan pendientes solo por tiempo. La forma de resolverlas es `pg_get_viewdef('schema.objeto'::regclass, true)`.

- Fórmula interna de las columnas `_weighted` de `oas_views.deals_assignments_metrics`.
- Definición de `time_tracking.delivery_cost_by_employee_monthly_mv` (19k de SQL): cómo arma `delivery_cost` y `staffing_delivery_cost` por empleado.
- Definición de `time_tracking.company_delivery_utilization_employee_monthly_mv` (11k): cuál de las dos utilizaciones precalcula.
- Definición de `time_tracking.mv_master`: de dónde salen `salary_cost`, `standard_cost`, `weekly_days` y `working_hours`, que son los insumos de todo el costo imputado.
- Cómo `view_project_metrics_monthly` calcula `cor_revenue_share` y `operating_revenue_share`, y si coincide con el prorrateo por participación de ingreso del Power BI.
- Definiciones completas de las vistas de compensaciones: qué componentes integran `total_compensation_cost`.

- Fórmulas de `compensations.view_headcount_plan`, `finance.view_salary_cost` y `parameters_info` (existencia ya verificada 2026-09-28).

- ~~Reconciliación del pool de HR en la MV~~ — **resuelto 2026-10-01**: cierra exacto, ver `control-center-pnl.md`.

## B) Solo las puede contestar Augusto

Decisiones de negocio o conocimiento que no está en la base.

**Definiciones en disputa**

- **Bench.** Hay tres definiciones conviviendo: umbral 70 en Staffing Center, 0,70 con población distinta en el Power BI, y el bench de recruiting del scorecard. ¿Cuál es la oficial, o cada una tiene su uso legítimo?
- **El factor 2,5 de `target_revenue`** está hardcodeado en `view_project_metrics_monthly`. ¿De dónde sale y cada cuánto se revisa?

**Vigencia**


- ¿Sigue vigente la equivalencia FEMSA/KOF y el recorte a Portfolio 1–5 en la pantalla de alineación?
- ¿Qué versión del Power BI y de las apps es la de referencia cuando dos fórmulas difieren?
- Baseline de commit para Q4 2026: todavía no está cargado (al 28/09 solo existe `revenue_commit_q3`).

**Semántica**

- Qué significan los niveles 1–3 de skills (`level_score`) y cuánto dura la vigencia de una respuesta.
- Qué significan `orientation_score` (`exceeds` / `meets` / `partially_meets`) y `promotion_readiness` (`not_ready` / `ready_soon` / `ready_now`), y si committee es la evaluación final. Los valores ya están verificados; falta la definición de negocio.
- Qué define cada color de `people.status` y quién resuelve las acciones.
- Qué son en el negocio la capitalización (`employee_salary_impact_recovery`) y el bonus reversal (`employee_bonus_recovery`), y qué representa un cost transfer. **El cálculo ya está verificado**: entran a `hr_costs_monthly` con signo negativo los dos primeros (ver `control-center-pnl.md`); falta la definición de negocio.
- Qué son los montos de `finance.finance_salaries` en meses con `forecast = true`: ¿proyección, budget o carga anticipada?
- Qué expande la sigla RDG y quién opera aprobación y pago.

**Responsables**

Casi todos los dominios identifican roles (`account_lead`, `delivery_lead`, `director`, `hrbp`, `approver_id`, `authorizer_id`) pero ninguna consulta demuestra quién decide qué. Si querés que la skill sepa a quién mandar una pregunta, hay que escribirlo a mano.

## C) Deuda de la skill

- `references/metrics.md` y `references/entities.md` vienen de la versión anterior y todavía cubren solo revenue. Conviene revisarlos ahora que hay más dominios.
- No hay archivo de golden questions: diez preguntas con su número correcto, para correr después de cada cambio grande y detectar regresiones.
