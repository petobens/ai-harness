# Golden questions

Preguntas con su número de referencia, para correr después de un cambio grande
en la skill, en una vista o en una query. Salen de las validaciones de MBR
Report contra los decks del MBR de agosto 2026 y del QBR Q3 2026 (septiembre).

**Los meses ya cerrados pueden moverse un poco** por datos cargados después del
freeze (bajas nuevas, reclasificaciones). Una diferencia chica no prueba por sí
sola una regresión: revisar cambios de datos, alcance y fórmula antes de
aceptarla. Al lado de cada número está lo que se sabe que lo mueve.

## People (`people.md`)

| Pregunta | Referencia | Fuente / nota |
|---|---|---|
| Headcount promedio de agosto 2026 | **192,9** (deck 193) | promedio diario de activos |
| Turnover voluntario L12M a septiembre 2026 | **36 bajas / 20,0%** | exacto contra el deck |
| Regrettable L12M a septiembre 2026 | **21 / 11,7%** (deck 12%) | exacto; el deck redondea |
| Exits de agosto 2026 | **5** | |
| Exits de septiembre 2026 | 8 (deck 7) | una baja involuntaria cargada después |
| Headcount de cierre de septiembre 2026 | 191 (deck 192) | misma causa |
| Salary difference de exit interviews, 12 meses a septiembre 2026 | **9 / 9 / 7 / 3** | por fecha de entrevista, sin N/A |
| eNPS de las 19 encuestas de 2026 (todas y "excl. <3 months") | iguales al reporte de eNPS | regla de los 3 meses de `people.md` |
| Delivery Mutters, promedio de septiembre 2026 | **149** | delivery mix de oct 25 = 164 = 132 + 32 |
| Activos hoy (2026-11-06) con `status = 'Active'` vs por fechas | 210 vs **203** | si dan igual, se está contando mal o no hay ingresos futuros |
| Organigrama 2026-11-05 | **203 activos, 57 managers, 7 capas** | `supervisor_id` |

## Lever (`lever.md`)

| Pregunta | Referencia | Nota |
|---|---|---|
| Hired, septiembre 2026 | **12** (deck 13) | archivados Hired |
| Offers sent, septiembre 2026 | **13** (deck 13) | la última por oportunidad, sin drafts |
| Offers accepted, septiembre 2026 | **12** | |
| Current Bench al 2026-11-06 | **22** | foto de hoy, cambia todos los días |
| Current Bench al cierre de septiembre 2026 | **19** (deck 21 "active external bench") | reconstruido desde el archivo actual de cada oportunidad |

## P&L y delivery (`control-center-pnl.md`)

| Pregunta | Referencia | Nota |
|---|---|---|
| Revenue PS de agosto 2026 | **1.005K** (deck 1.003K) | BU 3, vista del P&L |
| Delivery gross margin PS de agosto 2026 | **48,9%** (deck 48,8%) | recalculado sobre totales |
| Capacidad de Ops, agosto 2026 | **22,8K h** (deck 22,9K) | |
| Ops billable, agosto 2026 | **131** | |
| Gross margin PS de agosto 2026 | 32,5% (deck 28,7%) | difiere: reclasificación de BizOps / Habit posterior al freeze |
| Bench de Mutters, agosto 2026 | 13 (deck 9) | difiere: reclasificación de roles |
| Rev por Ops billable, agosto 2026 | 7,7K (deck 8,1K) | **no reproducido**: no usar como referencia |

Faltan referencias de revenue / forecast / commit (`revenue.md`) y de staffing
(`staffing.md`).
