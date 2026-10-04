# Revenue y pipeline

Dominio original de la skill, ya verificado contra la base. Schemas `pipeline` y `hubspot`.

## La regla de oro

**El forecast es `pipeline.view_revenue.realistic_amount`, nunca `pipeline.revenue.amount`.**

Cuando alguien pide "el revenue" o "el forecast" de un mes o un Q, la respuesta es la suma de `realistic_amount`. Sumar `amount` infla el forecast — en octubre 2026 la diferencia es de ~1,85M contra ~1,12M.

Las tres versiones del mismo monto, con el nombre que se usa internamente:

| Columna | Nombre interno | Qué pondera |
|---|---|---|
| `realistic_amount` | **Forecast** | Solo los deals con tasa realista ≥ 60. El resto va a 0. Es el número oficial. |
| `realistic_amount_old` | **Full weighted** | Pondera todo por su tasa, sin umbral. Incluye etapas tempranas. |
| `amount` | **Unweighted** | Monto pleno del deal, sin ponderar. Techo del pipeline. |

Los tres son legítimos y se reportan juntos a veces, pero nunca hay que mezclarlos sin decir cuál es cuál.

---

## Entidades

| Entidad | Tabla base | ID | Qué es |
|---|---|---|---|
| Deal | `hubspot.deals` | `deal_id` | Oportunidad comercial en HubSpot |
| Project | `oas_views.projects_joined` | `project_id` | Proyecto en ejecución (OAS) |
| Account | `oas_views` / `hubspot.deals.account_id` | `account_id` | Unidad de facturación |
| Client | derivado | `client_id` | Empresa madre; un client puede tener varias accounts |
| Company | `hubspot.deals_companies` | `company_id` | Firmográficos de HubSpot (industria, país, empleados) |

Una fila de revenue viene **o de un deal o de un proyecto**, nunca de ambos. Los flags `is_hubspot` / `is_project` lo indican, y `related_id` / `related` dan el identificador y nombre unificados — usar esos dos para agrupar sin ramificar por origen.

URL de un deal en HubSpot: `https://app.hubspot.com/contacts/22714877/deal/{deal_id}`

Detalle completo en `references/entities.md`.

---

## Cadena de derivación

```
hubspot.deals ─┐
               ├─> pipeline.deals_info ──> pipeline.deals_revenue ─┐
hubspot.line_items ──> pipeline.line_items_revenue ───────────────┤
                                                                   ├─> pipeline.revenue ──> pipeline.view_revenue
pipeline.manual_revenue (carga manual por proyecto) ───────────────┘                              │
                                                                                                  ├─> view_revenue_mv (copia rápida)
                                                                                                  └─> revenue_monthly_mv (agregado mensual)
```

Puntos clave de esa cadena:

- **Grano diario, solo días hábiles.** El monto total del deal se reparte proporcionalmente entre los días hábiles de cada mes del período. Un mes parcial recibe la fracción de días hábiles trabajados.
- **Corte histórico en 2024-01-01 solo del lado deals.** No hay revenue derivado de deals antes de esa fecha, pero `view_revenue` **sí tiene 2022 y 2023** del lado proyecto: 3,91M y 3,18M, con grano mensual en vez de diario. Vienen de `manual_revenue`.
- **`kickoff_date` pisa a la fecha de cierre como fecha de inicio** del reparto diario. Lo que importa operativamente es que el deal tenga kick off: desde el mes del kick off el revenue se activa al 100%.
- **`manual_revenue` sigue vigente.** Se carga a mano cuando no se sabe si el revenue va a venir de un deal. El grueso (344 de 370 filas, 7,09M) es la historia 2022–2023 previa a HubSpot, pero se puede seguir cargando. Las filas en 0 que llegan hasta fin de 2026 son de la unidad de negocio **Habit**, que no tiene revenue propio y existe ahí para prorratear costos — no las trates como un error de carga.
- **Closed Lost nunca entra.** `stage_id = 7` y `stage_id IS NULL` se filtran aguas arriba, así que `view_revenue` ya viene limpia. No hace falta volver a filtrarlo.
- **Deals con `line_item_revenue = true`** se calculan desde sus line items, no desde el monto del deal. Se excluyen del camino de `deals_info` para no duplicar.

---

## Deals (HS): cuenta genérica + compañía de HubSpot [VERIFICADO 2026-09-28]

Algunos deals están cargados sobre la **cuenta principal de un portfolio** (la cuenta que figura en `oas.areas.main_account_id`) y la empresa real está en la compañía de HubSpot. **`oas_views.deals_resolved`** (vista, una fila por deal) los resuelve. Es la misma regla, con los mismos IDs y nombres, que usa el Power BI.

Cómo la arma la vista (leído de su definición):

- `is_hs = true` cuando la cuenta del deal es la cuenta principal de un área **y** el deal tiene compañía en `hubspot.deals_companies`.
- Portfolio del deal HS: `hubspot.deals.portfoliobu`, o si no el área de la cuenta principal.
- Si la compañía ya está mapeada a un cliente/cuenta reales para ese portfolio (`hubspot.view_deals_companies`), usa esos IDs y nombres.
- Si no, crea una entidad sintética: cliente `(HS) <compañía>` con `client_id = -company_id`, y cuenta `(HS) <compañía>` con `account_id = -(company_id * 100000 + portfolio_id)`. **Los IDs negativos son esos sintéticos, no errores.**
- Logo de la compañía, país de la compañía (vía `oas.countries` o `oas.country_aliases`) y región por continente; BU y área del portfolio.
- Para deals no HS devuelve los valores originales del deal.

```sql
LEFT JOIN oas_views.deals_resolved rs ON rs.deal_id = vr.deal_id AND rs.is_hs
-- account_id:  CASE WHEN rs.deal_id IS NOT NULL THEN 'HS' || rs.account_id::text ELSE <cuenta del proyecto o deal>::text END
-- account:     COALESCE(rs.account, <cuenta>)
-- client:      COALESCE(rs.client, NULLIF(vr.client, ''), <cliente>)
-- portfolio:   COALESCE(rs.portfolio, <area>)
-- country/region: los de rs cuando hay match, si no los de la cuenta
```

- El `account_id` de esos deals se expone como texto con prefijo **`HS`** para que no choque con los IDs de `oas.accounts`. Al agrupar por cuenta, tratar `account_id` como texto.
- El **acceso** se sigue resolviendo con la cuenta original del proyecto o deal (`access_account_id`), no con la cuenta HS.
- Lo usan Control Center (revenue y deals), Pipeline Analytics, Pipeline Evolution, Commit Control, Commit Simulation y Ops Retention Target. Un análisis por cliente o cuenta que no aplique esta regla no va a coincidir con esas pantallas.

---

## Tasas de conversión

`view_revenue` calcula tres escenarios (`pessimistic`, `realistic`, `optimistic`). La tasa aplicada sigue esta precedencia:

1. `hubspot.deals.conversion_rate_manual` si el deal la tiene cargada (override manual, gana siempre).
2. 100% si el revenue es de un mes pasado o del mes en curso **y** `kickoff = true`. El kick off es el disparador: una vez que ocurrió, el revenue de ese mes en adelante deja de ponderarse.
3. La tasa de `hubspot.conversion_rates` según el par (`stage_id`, `type_id`).
4. 100% si no matchea nada.

**Regla del umbral 60:** si la tasa realista resultante es menor a 60, `realistic_amount` se fuerza a **0**. Esto no aplica a los escenarios pesimista ni optimista. Es la diferencia entre `realistic_amount` y `realistic_amount_old` (esta última es el cálculo viejo, sin umbral, que sigue disponible para comparar).

Efecto práctico: los deals en etapas tempranas (Open Deal, In Analysis, Proposal Sent para New Business) aportan 0 al revenue realista, aunque sí aparecen en el pipeline sin ponderar.

Matriz completa de tasas en `references/metrics.md`.

---

## Catálogos

**Stages** (`hubspot.deals_stages`, con `stage_order` para ordenar en visualizaciones):

| id | stage | order |
|---|---|---|
| 10 | Target Leads | — |
| 1 | Open Deal | 2 |
| 2 | In Analysis | 3 |
| 5 | Proposal Sent | 4 |
| 4 | Decision Maker Bought-In | 5 |
| 3 | Contract Negotiation | 6 |
| 11 | Committed | 7 |
| 6 | Closed Won | 8 |
| 7 | Closed Lost | 1 |

**Types** (`hubspot.deals_types`): 1 New, 2 Renewal, 3 XSell, 4 Upsell.

Ojo: `stage_order` no sigue el orden de los ids, y Closed Lost tiene order 1. Ordenar siempre por `stage_order`, nunca por `stage_id`.

---

## Qué tabla usar

| Necesidad | Objeto | Nota |
|---|---|---|
| Número exacto, cálculo en vivo | `pipeline.view_revenue` | Fuente de verdad. Más lenta (varios joins). |
| Dashboards, exploración, queries grandes | `pipeline.view_revenue_mv` | Materializada, ~40k filas. Puede estar desactualizada. |
| Agregado mensual listo | `pipeline.revenue_monthly_mv` | `revenue` = realista, `unweighted_revenue` = sin ponderar. |
| Comparar versiones en el tiempo | `pipeline.revenue_versions` | Snapshots por `version_date`; la usa Pipeline Evolution. Filtrar `version_date` y `date`. |
| Comparar forecast vs commit | `pipeline.revenue_commit_q3` | Baseline congelado. Usar esta para comparaciones. |
| Retention target (Ops) | `pipeline.retention_target` / `retention_target_monthly_mv` | **En uso** en Ops Retention Target y Control Center. Ver `metrics.md`. |
| Budget | `pipeline.budget_revenue`, `pipeline.budget` | **No usar por ahora.** |
| Simulaciones | schema `simulation_revenue` | Commit Simulation. Ver `tables/revenue.md` § Simulación. |

La materializada puede diferir de la vista si no se refrescó. Verificado en septiembre 2026: MV 1.142.010 vs vista 1.142.910. Para un número que va a una presentación, usar `view_revenue`; para explorar, la MV.

---

## Navegación

| Archivo | Contenido |
|---|---|
| `references/entities.md` | Entidades, joins, flags, catálogos completos |
| `references/metrics.md` | KPIs con fórmula SQL canónica y caveats |
| `references/tables/revenue.md` | Schema `pipeline` tabla por tabla |
| `references/tables/hubspot.md` | Schema `hubspot` tabla por tabla |

---

## Errores comunes

- **Sumar `amount` en lugar de `realistic_amount`** → forecast inflado.
- **Olvidar el filtro de fechas.** `view_revenue` contiene revenue futuro hasta 2028 y también 2022–2023 con grano mensual. Cualquier query sin rango mezcla tres cosas distintas.
- **Usar `price` de un line item como si fuera USD.** Puede estar en ARS. Siempre `price * quantity`.
- **Volver a filtrar Closed Lost.** Ya está excluido; el filtro extra no rompe nada pero confunde.
- **Ordenar stages por `stage_id`.** Usar `stage_order`.
- **Comparar contra `realistic_amount_old` sin aclararlo.** Son dos definiciones distintas de la misma métrica.
- **Consultar `revenue_versions` sin filtrar `version_date`.** Son ~40k filas por versión y 40 versiones.
- **Usar `hubspot.deals_backup` o `line_items_backup`.** Son respaldos históricos, no la fuente actual.

---
---

## Decisiones confirmadas [SQL APP + confirmado por Augusto]

- `realistic_amount` **es** el forecast: todo lo que pondera 60% o más. `realistic_amount_old` es el full weighted y `amount` el unweighted.
- El **budget no se usa por ahora** (`budget_revenue`, `budget`). El **retention target sí**: es **solo de Ops** (Professional Services, BU 3) [confirmado por Augusto 2026-09-28]; Mixilo Services y HABIT Services no tienen target. Lo usan Ops Retention Target y Control Center. [actualizado 2026-09 desde el SQL de las apps]
- Los snapshots se analizan en `revenue_versions`. `revenue_versions_weekly` y `revenue_commit` (rolling) ya no existen en la base.
- `Target Leads` con tasa 100 es **intencional**: son cargas manuales, entran a valor pleno.
- Para comparar forecast contra compromiso, usar **`revenue_commit_q3`** (es la única tabla de commit).
- **HABIT ya tiene revenue.** [VERIFICADO 2026-09-28] HABIT Services (BU 5) suma en 2026 un forecast de ~59K y ~575K unweighted, sobre 27 fuentes (casi todo deals). Las filas en 0 de `manual_revenue` **siguen vigentes**: existen para prorratear costos de HABIT Internal (BU 6) [confirmado por Augusto 2026-09-28]. No son errores de carga, pero ya no vale "HABIT no tiene revenue".
- El **baseline de Q4 2026 todavía no está cargado**. Hasta que exista, `revenue_commit_q3` es el único congelado.
