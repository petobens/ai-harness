# Patrones de diagnóstico

Causas que ya aparecieron al investigar anomalías. Son hipótesis para probar
primero, no conclusiones: confirmarlas siempre con la base antes de reportarlas.

## Antes de empezar

- **Igualar alcance, período y fórmula** antes de llamar "error de datos" a una
  diferencia entre pantallas (Power BI, Control Center, Gross Profit,
  Scorecard).
- **Separar meses cerrados del forecast.** Cerrado = `forecast = false` en
  `compensations.view_parameters`. El mes en curso además cambia todos los días
  por el staffed forecast.
- **Mirar `refreshed_at`** o comparar MV contra vista: una MV sin refrescar
  explica diferencias chicas.

## Un dato que no se movió o parece viejo

Buscar en `oas.workflows_catalog` qué workflow escribe esa tabla (`writes_to`) y
mirar su última corrida exitosa en `oas.workflow_runs`. Para las materializadas,
el workflow es "DB: Refresh All". Ver `workflows.md`.

## Un dato que "no tiene sentido" en el origen

Un deal en una cuenta que nadie cargó, un cliente de USA sin impuesto o un
formulario que no se puede guardar suelen ser triggers de la base, no errores de
carga. Ver `workflows.md` § Reglas que impone la base.

## Salto grande en el forecast

Casi siempre es **un deal que cruzó el umbral de 60** de `realistic_rate` (por
cambio de stage, de tipo o por un `conversion_rate_manual`), no crecimiento
general del pipeline. Comparar por deal entre dos snapshots de
`pipeline.revenue_versions` (filtrando `version_date::date`) o contra
`view_revenue`, y ordenar por la diferencia de `realistic_amount`.

## Non-delivery cost que sube

Puede subir por **efecto mix sin que cambie el headcount**: una caída chica de
utilización produce una suba relativa más grande de la participación
non-delivery, y se amplifica si la gente con horas non-delivery es más senior
que la de delivery. Separar por persona: billable o no, seniority (step) y
cambio de horas delivery contra non-delivery.

## Margen que cambia hacia atrás

La región y el país se derivan en vivo, sin versionado. Si un margen histórico
cambió de un día para otro, buscar en `oas.accounts_audit_log` y
`clients_audit_log` cambios de `client_id`, `partner_id` o país
(`changed_fields ? 'client_id'`), con `changed_at` y `changed_by_email`.

## Países raros o márgenes altos por geo

- **Filas con costo y sin revenue** en países inesperados (Suiza, fila vacía):
  deals HS en preventa, con el país de la casa matriz o sin país en la compañía
  de HubSpot.
- **Diferencias de región entre revenue y márgenes:** desde nov 2026 deberían
  cuadrar al peso (la vista del P&L ya usa `deals_resolved`). Si no cuadran,
  revisar si la MV está refrescada y si un deal HS cambió de compañía o de
  portfolio. El detalle por persona (`delivery_cost_by_employee_monthly_mv`)
  todavía deja los deals HS en Argentina. Ver `control-center-pnl.md` § País y
  región.
- **Delivery margin muy alto en un país:** suele ser mix de BU (Mixilo) o meses
  forecast con revenue sin staffing. Comparar por gross margin y solo meses
  cerrados.

## Revenue que "falta"

- Deal con `dealstage` sin mapear en `hubspot.deals_stages`: queda con
  `stage_id` NULL y fuera del revenue. Es intencional para etapas muy tempranas.
- Deal con `line_item_revenue = true`: el revenue sale de los line items;
  revisar `hubspot.line_items_inconsistencies`.
- Line items en ARS: usar `price * quantity`, nunca `price`.
