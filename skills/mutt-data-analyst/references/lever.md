# Recruiting: schema `lever`

Las definiciones de este archivo salen de **Lever Pipeline**, una página de
Talent Center (2026-10-21 al 2026-11-02).
**Están acordadas con el equipo de Talent** y reemplazan las del Power BI
"Talent", que no daban los números de Lever. **[SQL APP, acordado con Talent]**

Siguen siendo definiciones de una pantalla, no KPIs validados por Augusto. Para
un número que va a una presentación, decir que sale de las reglas de Talent
Center. Si alguna regla de abajo no alcanza, preguntar en vez de inventar.

---

## Objetos [VERIFICADO 2026-11-06]

| Objeto | Qué tiene |
|---|---|
| `lever.opportunities_flat` | Una fila por oportunidad (30.543): `opportunity_id`, `contact_id` (la persona), `name`, `show_url`, `stage_id`, `archived_at`, `archive_reason_id`, `created_at`, `deleted_at`, `last_synced_at` |
| `lever.archive_reasons_flat` | `archive_reason`, `type`. `type = 'hired'` solo para el motivo `Hired` |
| `lever.opportunities_stage_history` | Cada cambio de etapa: `opportunity_id`, `to_stage_id`, `changed_at` |
| `lever.stages` / `stages_flat` | Catálogo de etapas (`stage_name`) |
| `lever.offers_view` | Ofertas: `id`, `opportunity_id`, `status` (`draft`, `sent-manually`, `signed`, `declined`), `created_at`, `sent_at` |
| `lever.offers_fields` | Campos de la oferta por `field_label`: monto, moneda, tipo de ingreso, step, fecha de inicio prevista |
| `lever.forms_fields` | Formularios por `form_name` / `field_name` / `field_value_raw`. Los que se usan: **Hired Metrics** (desde 2026-03-19) y **Metrics Report** |
| `lever.feedback_fields` | Feedback de entrevistas (p. ej. `Cultural Interview` / `Rating`) |
| `lever.applications`, `postings_flat`, `postings_categories` | Búsqueda (`posting_name` = vacante) y `team` |
| `lever.pbi_scorecard_opportunities` | Vista del Power BI del Scorecard. La usa el Weekly Scorecard (bench de 120 días) |

**La sync no trae borrados.** `deleted_at` está NULL en todas las filas. Una
oportunidad borrada en Lever sigue en la base. Talent Center excluye por id la
`c1e9b460-137b-4457-8ae4-c5cf516781e4` (bench de 2023). Igual hay que filtrar
`deleted_at IS NULL`, por si se arregla.

## Fechas y formularios

- **Timestamps de Lever en hora Argentina (UTC−3)**:
  `(archived_at - interval '3 hours')::date`, o
  `date '1970-01-01' + floor((extract(epoch FROM ts) - 10800) / 86400)::int`.
- Las fechas de formularios (`Hired Date`, `Start Date`, `Openning Date`, así
  escrito) vienen en **milisegundos epoch como texto** y son fecha pura, sin
  corrimiento horario:
  `date '1970-01-01' + (field_value_raw::bigint / 86400000)::int`.
- De cada formulario se toma **el último por oportunidad**
  (`DISTINCT ON (opportunity_id)` con
  `ORDER BY opportunity_id, created_at DESC, form_id DESC`).
- Gender, University, Origin y Country se toman de Hired Metrics y, si faltan,
  del último Metrics Report. En Metrics Report, Country se llama `Location`.
- **Step** normalizado a IC1–IC5 / M1–M3 / S1–S2. Nombres viejos: JR → IC1, Semi
  Senior → IC2, Senior → IC3, Associate Manager → M1, Manager → M2.

## Métricas

| Métrica | Definición |
|---|---|
| **Opportunities** | oportunidades con algún cambio de etapa en el período (actividad), no solo las creadas |
| **Archived** | por fecha de archivo |
| **Hired** | archivadas con motivo de `type = 'hired'`, por fecha de archivo |
| **Started** | `Start Date` del formulario Hired Metrics en el período |
| **Offers Sent** | ofertas sin `draft`, con `sent_at` en el período (si falta, `created_at`). **La última por oportunidad** |
| **Offers Accepted** | `status = 'signed'` o la oportunidad quedó archivada como Hired |
| **Offers Declined** | `status = 'declined'` o motivo `Hire but offer Declined`, aunque después pase a Bench |
| **Time to Hire / Fill** | `Openning Date` → `Hired Date` / `Start Date` del formulario. Mediana y n. Sin fecha, el caso queda afuera |
| **TTH desde Intro Call** | desde la **última** Intro Call entre Openning Date y Hired Date (stage `3188d2a9-00e2-443e-9c53-f38842d702ff`). Los tramos negativos se descartan |

- **Hired y Started son definiciones separadas a propósito.** Un error de carga
  (p. ej. Start Date con motivo Underqualified) lo corrige Hiring en Lever, no
  la query.
- **Step, Gender, Country y University filtran solo Hired / Started / tiempos**,
  nunca ofertas ni opportunities. En el Power BI dejaban afuera los rechazos y
  daban 100% de aceptación.
- **Montos en USD:** ARS ÷ `compensations.view_parameters.official_usd` del mes
  de envío (desde 2023-01; antes no hay USD). Otras monedas (p. ej. UYU) quedan
  sin USD. El Power BI usaba un 1.490 fijo.
- **Salario pedido** = último Metrics Report con salario numérico.
  **Ofrecido** = última oferta del período. En medianas, solo USD 700–10.000.
  Gap = mediana de (ofrecido ÷ pedido − 1) de la misma persona.

## Funnel

- **Conversion Funnel** = cohorte de quienes entraron (New lead o New applicant)
  en el período, y hasta qué paso llegaron (llegó o pasó). Pasos: New → Reached
  out → Responded (solo sourcing) → Intro Call → Technical (interview o exam) →
  Cultural fit → Proposal → Hired (archivado Hired, en cualquier fecha).
- CR de un paso = personas en el paso ÷ personas en el paso anterior de su
  camino (applicants y sourcing tienen caminos distintos).
- Contacted, Top grading, Leadership y las etapas de cliente no son pasos del
  embudo: están en desuso o son opcionales.
- **Current Pipeline** (foto de hoy): activas sin archivar, en su etapa actual,
  que entraron a esa etapa en los últimos 90 días. Las más viejas siguen
  abiertas en Lever pero no se mueven (87% de New applicant).
- **Stage Outcomes**: la misma cohorte, partida en Moved on / Still here /
  Dropped here. Los contratados no cuentan como Dropped, aunque en Lever también
  son archivados.

## Bench de recruiting (candidatos, no Mutters)

Una fila por persona (`contact_id`), con **su último archivo de bench**. Los
motivos de bench son `Bench`, `Hiring Bench*`, `Bench Exit*` y `Exit Bench*`.

| Categoría | Regla |
|---|---|
| **Current Bench** | el último archivo de bench tiene motivo exactamente `Bench`. **Es una foto de hoy, sin filtro de fecha** |
| **Bench Exits** | último archivo `Bench Exit*` o `Exit Bench*`, por fecha de archivo |
| **Hiring Bench** | último archivo `Hiring Bench*`, por fecha de archivo |

- **Una oportunidad posterior no saca a nadie del bench** (acordado con Talent
  el 2026-11-02): una presentación a cliente que no avanza no cambia nada.
- Exclusiones por nombre heredadas del Power BI: `magali gerbasi`,
  `Lautaro Tacchini`, `Lucas De Palma`, `Test`.
- Al 2026-11-06, Current Bench = 22 [VERIFICADO].
- **Es otra definición que la del Weekly Scorecard.** Ese bench son candidatos
  distintos archivados como `Bench` en los 120 días hasta el cierre, sobre
  `lever.pbi_scorecard_opportunities`. Antes de citar un bench, decir cuál es
  (ver también `staffing.md` § Definiciones).

## Validación [VERIFICADO 2026-11-06]

Septiembre 2026 con estas reglas: Hired 12, Offers sent 13, Offers accepted 12,
Offers declined 1. El deck del QBR Q3 dice 13 / 13.

- MBR Report (`mbr_hiring`) usa estas reglas desde el 2026-11-06. Antes daba 12
  / 12 / bench 13 con la regla del Scorecard.
- **Current Bench a un cierre pasado**: personas cuyo último archivo de bench
  hasta ese día tiene motivo `Bench`. Septiembre 2026 da 19 (deck 21). Es una
  reconstrucción: Lever guarda solo el archivo actual de cada oportunidad, así
  que un cierre viejo puede no coincidir con lo que se vio ese día.

## No está en la base

Time to hire / time to fill del People Monthly Report y women hire rate tal como
los presenta el deck. Hay un TTH / TTF desde formularios (arriba), pero los
formularios Hired Metrics existen recién desde 2026-03.

## Errores frecuentes

- Contar todas las ofertas de una oportunidad: va **la última** por oportunidad.
- Incluir drafts en Offers Sent.
- Confundir Hired (fecha de archivo) con Started (Start Date del formulario).
- Filtrar ofertas por Gender / Step / Country: deja afuera los rechazos.
- Cortar fechas de Lever en UTC.
- Mezclar el bench de recruiting (candidatos) con el bench de Mutters
  contratados (`staffing.md`).
- Convertir ARS con un tipo fijo.
