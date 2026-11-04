# Métricas y KPIs

Cada métrica trae definición, SQL canónico y caveats. Usar estas queries como
base en vez de escribir una nueva.

---

## Revenue mensual (realista)

- **Definición**: revenue proyectado ponderado por probabilidad de cierre. Es
  *el* número de revenue.
- **Fuente**: `pipeline.view_revenue.realistic_amount`
- **Grano**: diario, agregable a mes

```sql
SELECT date_trunc('month', date)::date AS month,
       SUM(realistic_amount) AS revenue
FROM pipeline.view_revenue
WHERE date >= date_trunc('month', CURRENT_DATE) - INTERVAL '11 months'
  AND date <  date_trunc('month', CURRENT_DATE) + INTERVAL '12 months'
GROUP BY 1 ORDER BY 1;
```

- **Caveats**: meses pasados tienen tasa 100 si `kickoff = true`, así que
  realista ≈ sin ponderar hacia atrás y la brecha se abre hacia adelante. Los
  deals con tasa realista < 60 aportan 0.

## Revenue sin ponderar (pipeline bruto)

- **Definición**: valor total de lo que hay en el pipeline, sin descontar
  probabilidad.
- **Fuente**: `pipeline.view_revenue.amount`
- **Uso**: solo junto al realista, para mostrar el techo. Nunca solo.

```sql
SELECT date_trunc('month', date)::date AS month,
       SUM(amount)            AS unweighted,
       SUM(realistic_amount)  AS realistic,
       SUM(realistic_amount) / NULLIF(SUM(amount), 0) AS weighting_ratio
FROM pipeline.view_revenue
WHERE date >= date '2026-01-01' AND date < date '2027-01-01'
GROUP BY 1 ORDER BY 1;
```

## Escenarios pesimista / realista / optimista

```sql
SELECT date_trunc('month', date)::date AS month,
       SUM(pessimistic_amount) AS pessimistic,
       SUM(realistic_amount)   AS realistic,
       SUM(optimistic_amount)  AS optimistic
FROM pipeline.view_revenue
WHERE date >= date_trunc('month', CURRENT_DATE)
GROUP BY 1 ORDER BY 1;
```

**Caveat importante**: el umbral de 60 aplica solo al realista. Por eso el
pesimista puede quedar por encima del realista en deals con tasa entre 0 y 59.
No es un bug del dato; es la definición.

## Revenue por tipo de negocio

```sql
SELECT date_trunc('month', date)::date AS month,
       type,
       SUM(realistic_amount) AS revenue
FROM pipeline.view_revenue
WHERE date >= date_trunc('year', CURRENT_DATE)
GROUP BY 1, 2 ORDER BY 1, 2;
```

## Revenue por cliente / account

```sql
SELECT client,
       SUM(realistic_amount) AS revenue,
       COUNT(DISTINCT related_id) AS sources
FROM pipeline.view_revenue
WHERE date >= date_trunc('month', CURRENT_DATE)
  AND date <  date_trunc('month', CURRENT_DATE) + INTERVAL '1 month'
GROUP BY 1
HAVING SUM(realistic_amount) > 0
ORDER BY revenue DESC;
```

## Headcount proyectado

- **Fuente**: `view_revenue.headcount` (nominal) y `realistic_headcount`
  (ponderado, mismo umbral 60)
- Mismo patrón que revenue. Sirve para planificación de staffing contra
  pipeline.

## Forecast vs commit

**Fuente: los planes `commit` de `simulation_revenue`** [VERIFICADO 2026-10-30].
Cubren todos los trimestres de 2026:

| Objeto | Qué tiene |
|---|---|
| `revenue_plans` | Cabecera: `plan_id`, `kind` (`commit`), `label`, `source` (`dynamic_target`, `legacy`, `simulation`), `simulation_name`, `snapshot_at`, `promoted_at`, `promoted_by` |
| `revenue_plan_months` | Qué plan rige cada mes: `plan_id`, `kind`, `period`, `replaced_by`, `replaced_at` |
| `revenue_plan_lines` | Líneas: `period` (date), `source_type`, `deal_id`, `project_id`, `account_id`, `business_unit`, `portfolio`, `type`, `stage`, `amount`, `snapshot_amount`, `snapshot_unweighted`, `revenue_mode`, `origin`, `is_removed`, `is_user_edited` |

- **El commit vigente de un mes** es el plan cuya fila en `revenue_plan_months`
  tiene `kind = 'commit'` y `replaced_by IS NULL`. Hay uno por mes. Un plan
  reemplazado (`replaced_by` con valor) es historia: no sumarlo.
- **`amount` es el número comprometido.** `snapshot_amount` es el realista al
  momento del snapshot y `snapshot_unweighted` el unweighted. Pueden diferir
  porque el commit se edita a mano (`revenue_mode = 'manual'`,
  `is_user_edited`).
- Filtrar `NOT is_removed`.
- **El grano cambia por trimestre**: Q1 y Q2 (`dynamic_target`) vienen agrupados
  por BU × tipo, sin deal; Q3 (`legacy`) por cuenta y deal; Q4 (`simulation`)
  por deal y proyecto. **La comparación por deal solo es posible desde Q3.**
- El plan de Q3 coincide al peso con `pipeline.revenue_commit_q3`, que sigue
  existiendo. `pipeline.revenue_commit` (rolling) ya no existe.
- `revenue_admins` y `revenue_viewers` son las listas de acceso de la app; no
  son datos de revenue.

```sql
WITH commit AS (
  SELECT l.period AS month, SUM(l.amount) AS committed
  FROM simulation_revenue.revenue_plan_lines l
  JOIN simulation_revenue.revenue_plan_months m ON m.plan_id = l.plan_id AND m.period = l.period
  WHERE m.kind = 'commit' AND m.replaced_by IS NULL AND NOT l.is_removed
    AND l.period >= DATE '2026-01-01' AND l.period < DATE '2027-01-01'
  GROUP BY 1
), forecast AS (
  SELECT date_trunc('month', date)::date AS month, SUM(realistic_amount) AS forecast
  FROM pipeline.view_revenue
  WHERE date >= '2026-01-01' AND date < '2027-01-01'
  GROUP BY 1
)
SELECT c.month, c.committed, f.forecast,
       f.forecast - c.committed AS delta,
       (f.forecast - c.committed) / NULLIF(c.committed, 0) AS delta_pct
FROM commit c JOIN forecast f USING (month)
ORDER BY c.month;
```

Para comparar por deal (desde Q3), filtrar primero el commit vigente y excluir
las líneas removidas, como en el SQL anterior. Agregar cada fuente por
`deal_id` o `project_id` y mes antes de unirlas: `view_revenue` es diaria y
un join directo multiplicaría el commit mensual. Para Q1 y Q2, agregar ambas
fuentes por BU, tipo y mes.

## Retention target (Ops)

**Se usa.** [VERIFICADO 2026-09-28] **Es un target solo de Ops** (Professional
Services, BU 3) [confirmado por Augusto 2026-09-28]: Mixilo Services y HABIT
Services no tienen retention target, así que no calcular cobertura contra target
para esas BU. Hoy cubre ene–dic 2026, 10,5M en total. El módulo Ops Retention
Target (Revenue Center) y el Control Center comparan revenue contra
`pipeline.retention_target`.

- Revenue Center lee `pipeline.retention_target` por `date` y `account_id`,
  unido a `oas_views.accounts_joined` y **filtrado a `business_unit_id = 3`**.
- Control Center lee `pipeline.retention_target_monthly_mv` (`period_start`,
  `account_id`, `retention_target` y atributos de cuenta), recortado por el
  acceso del usuario, y en pantalla lo llama "Retention Target" / "Budget".

`pipeline.budget_revenue` y `pipeline.budget` siguen **sin uso**: ninguna app
los consulta. No incluirlos salvo pedido explícito.

## Evolución del forecast (snapshots)

- **Fuente: `pipeline.revenue_versions`**, un snapshot de `view_revenue` por
  `version_date`. Es la que usa Pipeline Evolution. [VERIFICADO 2026-10-30]
  Snapshots semanales, **los jueves** (11 h de Buenos Aires, guardado 14:00
  UTC), ~40–45k filas por versión: filtrar `version_date` siempre.
  `version_date` es **timestamp**: para filtrar por día, castear
  `version_date::date`.
- `pipeline.revenue_versions_weekly` **ya no existe en la base** [VERIFICADO
  2026-09-28]; era solo un depósito de datos y nunca fue la tabla de análisis.

```sql
-- Totales de los 3 pipelines en los últimos 10 snapshots, revenue de 2026
WITH last_versions AS (
  SELECT DISTINCT version_date FROM pipeline.revenue_versions
  WHERE date >= DATE '2026-01-01' AND date < DATE '2027-01-01'
  ORDER BY version_date DESC LIMIT 10
)
SELECT rv.version_date,
       SUM(rv.amount)               AS unweighted,
       SUM(rv.realistic_amount)     AS forecast,
       SUM(rv.realistic_amount_old) AS full_weighted
FROM pipeline.revenue_versions rv
JOIN last_versions lv USING (version_date)
WHERE rv.date >= DATE '2026-01-01' AND rv.date < DATE '2027-01-01'
GROUP BY 1 ORDER BY 1;
```

Convenciones de Pipeline Evolution: análisis solo sobre revenue de 2026, los
snapshots guardados **más el pipeline vivo** (`view_revenue`, con clave
`'live'`), y el Forecast como pipeline principal del que parten los cortes.
Filtrar siempre `version_date` y rango de `date`.

`revenue_versions_changes` expone los cambios entre versiones.

## Matriz de tasas de conversión

`hubspot.conversion_rates`, por (`stage_id`, `type_id`). Valores enteros 0–100.

| stage | New | Renewal | XSell | Upsell |
|---|---|---|---|---|
| Open Deal (1) | 5 | 25 | 15 | 20 |
| In Analysis (2) | 15 | 60 | 25 | 55 |
| Proposal Sent (5) | 25 | 74 | 35 | 71 |
| Decision Maker Bought-In (4) | 60 | 81 | 65 | 77 |
| Contract Negotiation (3) | 70 | 92 | 75 | 90 |
| Committed (11) | 97 | 97 | 97 | 97 |
| Closed Won (6) | 100 | 100 | 100 | 100 |
| Closed Lost (7) | 0 | 0 | 0 | 0 |
| Target Leads (10) | 100 | 100 | 100 | 100 |

(Tasas realistas. Pesimista y optimista difieren; consultar
`hubspot.conversion_rates` directo si hacen falta.)

Con el umbral de 60, aportan 0 al revenue realista [VERIFICADO 2026-10-06]: New
y XSell hasta Proposal Sent inclusive, Renewal solo en Open Deal, Upsell en Open
Deal e In Analysis (55).

`Target Leads` (stage 10) está en 100 a propósito: son cargas manuales y entran
al forecast a valor pleno. No tratarlo como dato sospechoso ni excluirlo.

`hubspot.conversion_rate_empiric` y `view_empiric_conversion_rate_ps` calculan
tasas observadas contra estas tasas teóricas.

---

## Convenciones de presentación

- Montos en miles con separador de miles, sin decimales.
- Porcentajes: la escala en la base depende del concepto (ver la tabla de
  escalas del `SKILL.md`: tasas 0–100, márgenes 0–1). Exponerlos siempre como
  decimal 0–1 y formatear con al menos un decimal (31,3%).
- Meses en el eje X ordenados cronológicamente, no alfabéticamente.
- Stages ordenados por `stage_order`.
- Al mostrar realista junto a sin ponderar, aclarar cuál es cuál: la diferencia
  es grande y se malinterpreta fácil.
