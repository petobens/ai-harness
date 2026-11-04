# Frescura de datos, workflows y reglas que impone la base

## Catálogo y corridas de workflows [VERIFICADO 2026-10-30]

Todas las cargas y alertas son workflows de Appsmith. No hay `pg_cron`.

- **`oas.workflows_catalog`**: `workflow_id`, `workflow_name`, `workspace`,
  `description`, `writes_to` (array de tablas), `slack_channel`,
  `schedule_cron`, `timezone` (America/Argentina/Buenos_Aires), `category`
  (`Write`, `Alert`, `Alert + Write`).
- **`oas.workflow_runs`**: una fila por corrida, con `started_at`,
  `finished_at`, `result` (`SUCCESS` / `FAILED`, en mayúsculas), `failed_step`,
  `error_type`, `error_message` y `duration`. Lo escribe el workflow "Monitor
  Workflow Runs" cada 15 minutos.

**Antes de dar un número que depende de una carga, chequear que la carga
corrió:**

```sql
SELECT c.workflow_name, c.schedule_cron, array_to_string(c.writes_to, ', ') AS writes_to,
       max(r.started_at) FILTER (WHERE r.result = 'SUCCESS') AS last_success,
       count(*) FILTER (WHERE r.result = 'FAILED' AND r.started_at > now() - interval '7 days') AS fails_7d
FROM oas.workflows_catalog c
LEFT JOIN oas.workflow_runs r ON r.workflow_id = c.workflow_id
GROUP BY 1, 2, 3
ORDER BY 1;
```

`workflow_runs` tiene datos desde el 2026-10-11.

## Cargas principales (hora de Buenos Aires)

| Workflow | Escribe en | Cuándo |
|---|---|---|
| API: Hubspot Deals | `hubspot.deals`, `oas.deals_assignments` | Cada 15 min, 7 a 21 h |
| API: Hubspot Companies | `deals_companies`, `deals`, `oas.countries`, `country_aliases` | 8, 12 y 16 h |
| API: Hubspot Line Items | `hubspot.line_items` | 2, 6 y 8 h |
| API: Hubspot Deals Stages | `hubspot.deal_stages_record` | 12 h, lunes a sábado |
| API: Hubspot Deals Owners | `hubspot.deals_owners` | 7 h, lunes a sábado |
| API Post: Line Item ARS Update | HubSpot (line items y deals) | 11:43 y 17:43 |
| DB: Refresh All | Refresca las materializadas | Cada hora (minuto 8), 8 a 21 h |
| DB: PipelineVersions | `pipeline.revenue_versions` | **Jueves 11 h** (se guarda 14:00 UTC) |
| DB: Expenses / Finance Salaries | `finance.expenses`, `finance.finance_salaries` | Todos los días, 10 h |
| DB: Deals Backup | `hubspot.deals_backup`, `line_items_backup`, `oas.deals_assignments_backup` | Martes 9 h |
| DB: Time Tracking Autosubmit | — | 18 h, lunes a viernes |
| DB: Hiring Checkup | `people.hiring_checkup` | 5 h |

Consecuencias:

- **Una materializada puede tener hasta una hora de atraso** entre las 8 y las
  21, y toda la noche fuera de ese rango. Para un número que va a una
  presentación, usar la vista.
- **"DB: Deals Backup" pisa semanalmente** `hubspot.deals_backup`,
  `hubspot.line_items_backup` y `oas.deals_assignments_backup`. No son historia
  confiable ni fuente de análisis. No extrapolar esa frecuencia a otros backups.

## Alertas que ya existen

Los workflows de categoría `Alert` mandan chequeos a Slack. Algunos: "Time
Tracking Health" (forms de time tracking y sueldo vs costo asignado), "BizOps
Data Checks", "Pipeline Alerts", "Staffing Overasigned", "Portfolio Bamboo vs
Time Report", "People Checks", "Gross Profit Check", "Deals Revenue", "Open
Deals Update". Si una pregunta es "¿hay algo mal en X?", estos chequeos son el
criterio vigente de "mal". Su lógica vive en Appsmith, no en la base.

## Reglas que impone la base (triggers) [VERIFICADO 2026-10-30]

| Tabla | Trigger | Qué hace |
|---|---|---|
| `hubspot.deals` | `set_default_account_id` | Si el deal llega sin `account_id`, le asigna la cuenta genérica. Ver `entities.md` § Cuenta por defecto |
| `hubspot.deals` | `follow_hubspot_portfolio` | Si el deal está en la cuenta genérica de un portfolio y cambia `portfoliobu`, lo mueve a la cuenta genérica del nuevo portfolio |
| `hubspot.deals` | `log_deal_changes` | Registra cambios en `hubspot.deals_audit` |
| `oas.clients` | `enforce_tax_for_country3` | Fuerza `tax = 0` en clientes de Estados Unidos (`country_id = 3`) |
| `oas.accounts`, `oas.clients`, `oas.projects` | `fn_*_audit_log` | Auditoría en `*_audit_log` (ver `entities.md`) |
| `time_tracking.dedications` | `validate_dedication_sum` | Rechaza cualquier insert, update o delete que deje un formulario con `SUM(dedication) <> 100` |
| `people.status` | `prevent_delete_if_submitted` | No deja borrar un status ya enviado |
| `pipeline.manual_revenue` | `log_insert_` / `log_delete_manual_revenue` | Registran altas y bajas en `pipeline.manual_audit` |
| `compensations.employee_area_allocations` | `validate_employee_area_allocation` | Exige que `allocation_pct` sume 1,00 por empleado y período |

Si un dato "no tiene sentido" (un deal en una cuenta que nadie cargó, un cliente
de USA sin impuesto), revisar primero estos triggers antes de suponer un error
de carga.
