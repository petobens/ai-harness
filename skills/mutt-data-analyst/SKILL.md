---
name: "mutt-data-analyst"
description: "Contexto de la base PostgreSQL de Mutt Data: revenue y pipeline de HubSpot, dedicaciones y time tracking, staffing y bench, costos de delivery, utilización, P&L por proyecto, compensaciones, people y development. Define entidades, métricas canónicas con su fórmula real y los errores frecuentes. Usar para cualquier consulta, análisis, KPI, dashboard o presentación sobre datos de Mutt Data — revenue, forecast, commit, horas, dedicaciones, costos, márgenes, headcount, bench, reviews o payroll."
---

# Mutt Data — contexto de datos

## Cómo usar esta skill

Este archivo tiene lo que vale para cualquier pregunta. El detalle de cada dominio está en `references/`: abrir el que corresponda antes de escribir SQL.

| Si la pregunta es sobre | Abrir |
|---|---|
| Revenue, forecast, pipeline, commit, deals, tasas de conversión | `references/revenue.md` |
| Horas reportadas, dedicaciones, formularios, costo imputado | `references/time-tracking.md` |
| Costo de delivery, utilización, márgenes, P&L por proyecto, completion | `references/control-center-pnl.md` |
| Staffing, asignaciones, headcount planificado, bench, vacantes | `references/staffing.md` |
| Performance reviews, skills por práctica (schema `development`) | `references/development.md` |
| Compensaciones, payroll, distribución de costos a áreas, people | `references/dominios-sin-verificar.md` |
| Joins y catálogos entre entidades | `references/entities.md` |
| Fórmula SQL de un KPI puntual | `references/metrics.md` |
| Columnas de una tabla concreta | `references/tables/` |
| Qué falta definir y quién lo define | `references/pendientes.md` |

---

## Dialecto: PostgreSQL (AWS RDS)

- Acceso read-only vía MCP `postgres` (`execute_sql`, `list_objects`, `explain_query`).
- `date_trunc('month', date)::date` para agrupar por mes; `to_char(date, 'YYYYMM')::int` para la clave `period` que usan varias vistas.
- Las materializadas las refresca un workflow de Appsmith que corre todos los días. No hay `pg_cron` en la base.
- Cuando no sepas la definición de una vista, leerla: `pg_get_viewdef('schema.objeto'::regclass, true)`. Es preferible a suponer la fórmula.

## Escalas: el mismo concepto viene en tres escalas distintas

Confundirlas es el error más caro de toda la base.

| Concepto | Dónde | Escala |
|---|---|---|
| Tasas de conversión, `dedication` de time tracking y staffing | PostgreSQL | **0–100** |
| `allocation_pct` del P&L | PostgreSQL | **0–1** (suma 1,00 por empleado y período, no 100) |
| Márgenes, `completion`, `realization`, desvíos relativos | PostgreSQL | **fracción 0–1**, ya dividida |
| Todo lo anterior expuesto en apps y reportes | Appsmith / Power BI | decimal 0–1, formateado como porcentaje |

Verificado: los 102 pares empleado-período de `employee_area_allocations` suman exactamente 1,0000, sin excepciones.

## Moneda

**El revenue está todo en USD y no hay conversión en ninguna tabla** de `pipeline`, `hubspot` ni `oas_views`: no existe columna de moneda ni de tipo de cambio.

La excepción son los line items: algunos se cargan con `price` en ARS y `quantity` = 1/tasa de cambio, de modo que `price * quantity` cierra en USD.

- **`price` de un line item no es comparable entre filas.** Usar siempre `price * quantity`.
- Los line items en ARS se reconocen por `quantity < 1`: 134 de 890, con mínima 0,000621 (tasa ≈ 1.610).
- **Esta regla no se extiende a compensaciones ni a RDG.** Esos dominios sí tienen `currency`, `official_usd` y parámetros `_ars` / `_usd` propios.

## Entidades núcleo

| Entidad | Tabla base | ID |
|---|---|---|
| Deal | `hubspot.deals` | `deal_id` |
| Project | `oas_views.projects_joined` | `project_id` |
| Account | `oas.accounts` / `oas_views.accounts_joined` | `account_id` |
| Client | `oas.clients` | `client_id` |
| Employee | `bamboo.employees` / `bamboo.employees_joined` | `employee_id` |

Una fila de revenue o de costo viene **o de un deal o de un proyecto**, nunca de ambos. Los flags `is_hubspot` / `is_project` lo indican y `related_id` / `related` dan el identificador unificado — usar esos para agrupar sin ramificar por origen.

**Verificado: los espacios de IDs no colisionan.** 291 proyectos y 1.479 deals, cero IDs compartidos. Resolver `related_id` contra ambos es seguro hoy, aunque nada en el schema lo garantiza a futuro.

Ojo con `hubspot.deals`: la columna del proyecto se llama **`projectid`, sin guion bajo**. No existe `project_id` en esa tabla.

URL de un deal: `https://app.hubspot.com/contacts/22714877/deal/{deal_id}`

## Schemas fuera de alcance

**[VERIFICADO 2026-09-28: existen en la base]** No usarlos para análisis, KPIs ni reportes salvo pedido explícito. Si una tabla de estos schemas parece responder la pregunta, buscar el equivalente vigente.

| Schema | Qué es | Equivalente vigente |
|---|---|---|
| `archive` | Backup, se va a borrar | — |
| `compensations_calculator` | Modelo viejo de simulación de aumentos | `compensations` |
| `dev` | Vistas para devs | — |
| `orgchart` | Organigrama, desactualizado | `bamboo.employees_joined` (`supervisor_id`) |
| `people_reporting` | Vistas que alimentan a People | `people`, `bamboo` |
| `performance_review` | Modelo viejo de skills y performance review | `development` |
| `public` | Sin uso (0 objetos) | — |
| `sales` | Sin uso | `hubspot`, `pipeline` |
| `security_tracking` | Solo lo usa Muttito | — |
| `staffy` | Lo usaron devs (0 objetos visibles) | — |
| `tech` | Del equipo tech | — |
| `sas` | Billing viejo, muerto | — |
| `vuriltek` | Billing viejo, muerto. **Excepción: `vuriltek.monedas`**, que sigue en uso (ver abajo) | — |
| `slack` | Sin uso (a confirmar) | — |

**`vuriltek.monedas` no se puede borrar ni ignorar [VERIFICADO 2026-09-28]:** `people.view_rdg` depende de ella como catálogo de monedas. Las otras dependencias sobre `sas` y `vuriltek` (`vuriltek.cashflow` sobre `sas.view_cobros` / `view_facturas_final`, `sas.view_facturas` sobre `monedas`) quedan todas dentro del billing muerto.

**`lever` (recruiting) está en uso, pero todavía no es fuente confiable de métricas.** Hoy es muy difícil sacar KPIs de ahí. No construir métricas de recruiting sobre `lever` sin validarlas antes con Augusto, y decirlo en la respuesta.

Los schemas de análisis son `bamboo`, `compensations`, `development`, `finance`, `hubspot`, `muttito`, `oas`, `oas_views`, `people`, `pipeline`, `simulation_revenue`, `time_tracking` y `time_tracking_old`.

## Año fiscal

Coincide con el calendario.

---

## Errores comunes, de cualquier dominio

- **Sumar `amount` en lugar de `realistic_amount`** cuando piden el forecast.
- **Olvidar el filtro de fechas.** `view_revenue` llega hasta 2028 y tiene 2022–2023 con grano mensual.
- **Usar `price` de un line item como si fuera USD.**
- **Mezclar las tres escalas** de la tabla de arriba.
- **Confundir enviado con aprobado** en formularios de time tracking.
- **Duplicar filas** al unir un agregado financiero con personas, o un formulario con sus líneas y sus resoluciones.
- **Recalcular un cociente promediando cocientes.** Márgenes, utilización y realization se recalculan sobre los totales.
- **Usar `revenue_versions_weekly` o `revenue_commit` (rolling).** Ya no existen: los snapshots están en `pipeline.revenue_versions` y el commit en `revenue_commit_q3`.
- **Agrupar por cuenta sin la regla de deals (HS)** de `oas_views.deals_resolved`: los totales por cliente o cuenta no van a coincidir con las apps ni con el Power BI.
- **Usar objetos `*_backup`** (`hubspot.deals_backup`, `line_items_backup`, `development.review_latest_backup`). Son respaldos históricos.
- **Usar un schema fuera de alcance** (tabla de arriba), en especial `performance_review` en lugar de `development`, o `compensations_calculator` en lugar de `compensations`.
- **Reproducir un umbral de pantalla como si fuera objetivo corporativo.** Los targets confirmados son gross margin 41% y delivery gross margin 60%; el 80% de utilización es solo semáforo. Ver `references/control-center-pnl.md`.
- **Tomar como cerrado cualquier mes anterior al actual.** Cerrado = `forecast = false` en `compensations.view_parameters`.
- **Reportar hacia afuera la utilización delivery.** La externa es `kpis_utilization`.

## Procedencia del contenido

Cada archivo de `references/` marca su nivel de evidencia:

- **[VERIFICADO]** — chequeado contra la base en esta sesión, con la fecha.
- **[CONFIRMADO POR AUGUSTO]** — definición de negocio dada por Augusto, con la fecha. Manda sobre cualquier otra fuente.
- **[SQL APP]** — tomado del SQL que corre en producción en una app de Appsmith o de una medida DAX del Power BI. Es la definición vigente de esa pantalla, no necesariamente la oficial de la compañía.
- **[SIN VERIFICAR]** — plausible pero no chequeado. No usarlo para un número que va a una presentación sin confirmarlo antes.
