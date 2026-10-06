# Development: performance reviews y skills

**[VERIFICADO 2026-09-28]** contra la base salvo donde se marca otra cosa.
`development` tiene **16 tablas y ninguna vista**: toda regla derivada
(completion, `needs_update`, "compartido") se calcula en el SQL de las apps, no
en la base.

**No confundir con `performance_review`**, que es el modelo viejo de reviews y
skills (ver "Schemas fuera de alcance" en `SKILL.md`). El modelo vigente es
`development`.

---

## Performance reviews

### Modelo

```text
review_cycles 1─N review_cycle_employees 1─1 self_reviews
                                         1─1 lead_reviews ─ lead_review_coreviewers (N)
                                         1─N peer_reviews
                                         1─1 committee_reviews
committee (por ciclo) 1─N committee_member
```

- **Grano de participación:** `review_cycle_employees`
  (`review_cycle_employee_id`), una fila por empleado y ciclo. Cero duplicados
  empleado-ciclo.
- Todas las reviews cuelgan de `review_cycle_employee_id`,
  **no de `employee_id`**. Para llegar a la persona, unir con
  `review_cycle_employees`.
- `self_reviews`, `lead_reviews` y `committee_reviews`: máximo 1 por
  participación.
- `peer_reviews`: hasta 4 por participación. El que escribe es
  `reviewer_employee_id`.
- `lead_review_coreviewers`: co-evaluadores del lead (`coreviewer_employee_id`),
  con `status` `pending` / `submitted`.
- En la UI, la peer review se llama **"Mutter Review"**. En
  `review_latest_backup` aparece como `review_type = 'mutter'`, con el mismo
  conteo que `peer_reviews`.

### Ciclos

| `review_cycle_id` | Ciclo | Estado |
|---|---|---|
| 7 | 2026 `mid_year` (01-01 → 06-30) | `active = true`, 155 participantes, share date 2026-09-07 |
| 8 | 2026 `annual` (01-01 → 12-31) | creado, `active = false`, **sin participantes todavía** |

`cycle_type` vale `mid_year` o `annual`. Fechas límite por etapa:
`self_review_due_date`, `lead_review_due_date`, `peer_review_due_date`,
`final_review_share_date`.

### Estados reales

| Tabla | Valores de `status` |
|---|---|
| `self_reviews` | `draft`, `submitted` |
| `lead_reviews` | `submitted`, `reopened` |
| `committee_reviews` | `submitted`, `reopened` |
| `peer_reviews` | `draft`, `submitted` |
| `lead_review_coreviewers` | `pending`, `submitted` |

**Ninguna tabla tiene un estado `shared`.**

### Trampas

- **"Compartido" se lee de `review_cycle_employees.final_review_shared`, no de
  `shared_at`.** `shared_at` existe en `lead_reviews` y `committee_reviews`,
  pero está vacío en todas las filas (0 de 155). En el ciclo 7,
  `final_review_shared = true` en 129 de 155 participaciones.
- **Comité: usar `review_cycle_employees.committee_id`.** Existe también
  `review_committee_id`, pero está vacío (0 de 155). `committee_id` está
  completo (155 de 155) y une con `development.committee` (9 comités).
- **La participación congela el perfil del ciclo:** `area`, `department`,
  `track`, `step`, `contract_type`, `working_hours`, `employment_status` y el
  líder (`lead_employee_id`). También las últimas fechas de cambio:
  `last_step_change_date`, `last_job_change_date` y
  `last_compensation_change_date`. Para comparar ciclos, usar estos campos y no
  `bamboo.employees_joined`, que muestra el rol actual.
- `review_latest_backup` es un **respaldo** del último payload de cada review,
  con tipos `self`, `lead`, `committee`, `coreview` y `mutter`. No usarlo como
  fuente de análisis.

### Escalas de los scores (texto, no números)

- **`orientation_score`**: `exceeds`, `meets`, `partially_meets`. En committee,
  ciclo 7: exceeds 34, meets 113, partially_meets 8.
- **`promotion_readiness`**: `not_ready`, `ready_soon`, `ready_now`. En
  committee, ciclo 7: not_ready 98, ready_soon 44, ready_now 13.
- **Scores de valores** (`value_data_nerds_score`,
  `value_open_team_players_score`, `value_take_ownership_score`,
  `value_positive_mindset_score`): son texto con la misma escala. En committee,
  ciclo 7, solo aparecen `exceeds` y `meets`. Cada uno tiene su `_comment`.
- `self_reviews` también tiene `orientation_score`, además de
  `career_preferences`. Para el resultado final, usar el de **committee**. Que
  committee es la evaluación final sigue siendo un supuesto: ver
  `pendientes.md`.
- **No promediar estos scores como números.** Si hace falta un índice, definir
  el mapeo explícitamente y declararlo en la respuesta.
- `private_general_comments` (lead y committee) es **privado**: no exponerlo en
  reportes ni apps de alcance amplio.

---

## Skills por práctica

### Modelo

```text
practices 1─N capabilities ─ capability_dependencies (capability_id → depends_on_capability_id)
practices 1─N skill_practice_forms (una por empleado y práctica) 1─N skill_responses (una por capacidad)
skill_requests: pedidos de un empleado para sumarse a una práctica
```

- **Prácticas activas (4):** AI/ML, Data Eng & Architecture, MarTech y
  Cross-cutting.
- **Capacidades activas por práctica:** AI/ML 28, Data Eng & Architecture 34,
  MarTech 15, Cross-cutting 16. `capability_type` vale `Skill` (57) o
  `Technology` (36).
- **Formularios:** 604, todos activos. Corresponden a 151 empleados × 4
  prácticas, y no hay duplicados empleado-práctica activos.
- **Estados de `skill_practice_forms.status`:** `pending` (99), `in_progress`
  (5), `submitted` (500). `needs_update` **no es un estado guardado**: lo
  calcula la app cuando aparecen capacidades activas sin respuesta en un
  formulario `submitted` [SQL APP].
- **Respuestas:** `skill_responses` tiene una fila por formulario y capacidad,
  sin duplicados.
  - `level_score` va de 1 a 3: 6.640 respuestas con 1, 3.477 con 2 y 1.560 con
    3.
  - `interest` y `recent` son booleanos, con 1 y 2 nulos respectivamente.

### Métricas [SQL APP]

- **Capacidad contestada:** `level_score` entre 1 y 3 **con** `interest` y
  `recent` no nulos.
- **Completion de un formulario:**
  `100 × contestadas / capacidades activas de la práctica`, con un decimal. Está
  en escala 0–100: al exponerlo en una app, dividir por 100.
- `GetAIGlobalSkills` promedia solo respuestas completas, mientras que
  `GetBenchMutters` cuenta por nivel válido sin exigir `interest` ni `recent`.
  **Los dos conteos difieren.**
- No hay tabla de skills requeridas por deal.

---

## Relación con `bamboo.development`

`bamboo.development` (335 filas) es el historial de desarrollo que viene de
BambooHR. **No es el mismo modelo** que `development.*`. El ID Card de Mutters
Directory lee reviews y skills de `development.*`.
