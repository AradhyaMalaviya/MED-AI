# 🐛 BUGFIX_REMEDIATION_PLAN.md
# MediCare AI — Bug Audit Remediation Plan

> **Date:** 2026-06-26
> **Source:** Manual bug audit (8 confirmed issues across backend, frontend, tests, and docs)
> **Status:** Draft — ready for execution
> **Important caveat:** This plan was written from your project documentation plus the bug report you supplied, not a live read of `app.py` / `main.js` / `test_observability.py`. Code snippets below are **illustrative patterns**, not verbatim diffs — confirm against your actual line numbers with `grep`/your editor before applying.

---

## 0. Why This Document Exists

Several items below directly contradict "RESOLVED ✅" / "COMPLETED" / "PASSED" entries in your existing docs:

| Existing doc | Claim that this audit contradicts |
|---|---|
| `claude.md` | "Training-serving skew: None (Skew fully resolved) ✅" |
| `PRD.md` | "Feature Preprocessing: ✅ Functional... resolving training-serving skew" |
| `audit_report.md` | "Request Timing Logs... raw input payloads/PHI are omitted from logging outputs. COMPLETED" |
| `audit_report.md` | "Expand /health... without leaking paths or system details. COMPLETED" |
| `PROGRESS_AND_STATUS.md` | "...ensuring patient-identifying data remains unlogged" |

This isn't a criticism of the docs — it just means **doc correction is part of this plan**, not an afterthought (see §7).

---

## 1. Executive Summary

| ID | Original Item | Area | Title | Severity | Effort | Retrain Needed? |
|---|---|---|---|:---:|:---:|:---:|
| BUG-101 | Backend #1 | ML Pipeline | `outcome_variable` heuristic / feature leakage | 🔴 CRITICAL | High | ✅ Yes |
| BUG-102 | Backend #2 | ML Pipeline | Redundant double scaling of vitals | 🟠 HIGH | High | ✅ Yes |
| BUG-103 | Backend #3 | API | `model` param silently ignored | 🟡 MEDIUM | Low (minimal) / High (full) | ❌ No |
| BUG-104 | Frontend #1 | UI | Hamburger menu has no JS handler | 🟡 MEDIUM | Low | ❌ No |
| BUG-105 | Frontend #2 | UI | Confidence type mismatch (string vs number) | 🟢 LOW | Low | ❌ No |
| BUG-106 | Tests #1a | Tests | Vacuous assertion in PHI logging test | 🟠 HIGH | Low | ❌ No |
| BUG-107 | Tests #1b | Backend | **Real** PHI leak into logs (`age`, `gender`) | 🔴 CRITICAL | Low | ❌ No |
| BUG-108 | Docs/API #1 | Backend | `/health` never reports degraded state | 🔴 CRITICAL | Low–Med | ❌ No |

**Read this first:** BUG-106 and BUG-107 are two halves of one finding — the test that was supposed to catch PHI leakage in logs is broken in a way that makes it pass even though the leak is real. Fix both together.

---

## 2. Cross-Cutting Findings (read before starting)

1. **High test coverage didn't catch any of these.** 60 tests / 86% line coverage measures *lines executed*, not *correctness of what's asserted*. BUG-106 is the clearest example — the line ran, the assertion technically passed, and it told you nothing. After each fix below, the new tests must assert the *right* thing, not just exercise the code path.

2. **The "outcome_variable" / "risk_level" question (PRD Q-005) deserves a second look.** Your PRD marked this "RESOLVED ✅ (Required input features for `best_model.pkl`)" — but a feature that has to be *guessed via a heuristic at serving time* because the real value isn't knowable for a new patient is a sign the original modeling decision should be revisited, not just patched. See BUG-101.

3. **Dataset is small (349 rows).** Whatever fix you choose for BUG-101/102 will change the effective feature set the model trains on. Re-validate accuracy honestly afterward — don't assume the existing "≥60% top-1" target documented in `PRD.md` §1.4 still holds without re-measuring. If you've published an accuracy figure anywhere (README, LinkedIn, etc.), treat it as provisional until you've re-run validation post-fix.

4. **BUG-108 interacts with a known, already-flagged CI limitation.** `observability.md` already notes that `.pkl` files are gitignored, so the Docker image built in CI has no models loaded. Right now `/health` would report `200 healthy` for that broken image anyway — so the existing "Docker image builds, /health returns 200" gate in `quality_gates.md` may have been passing for the wrong reason. Fixing BUG-108 will make this visible (a CI Docker smoke-test will start correctly failing) — that's a feature of the fix, not a regression.

---

## 3. Detailed Bug Analysis & Fix Plan

### 🔴 BUG-101 — `outcome_variable` heuristic mismatch

**Confirmed issue:** `app.py` sets `outcome_variable = 'Positive' if symptom_count >= 2 else 'Negative'` at prediction time. The model was trained on the *real* `outcome_variable` column in `Cleaned_Dataset.csv`, which doesn't perfectly correlate with symptom count (some 2-symptom rows are "Negative", some 1-symptom rows are "Positive").

**Root cause:** This is deeper than a simple skew bug. `outcome_variable` is real recorded data the model learned a relationship from — but it isn't something a new patient can provide at prediction time (you can't ask "what was your test outcome?" when the whole point is to predict the diagnosis). Faking it with a heuristic means:
- The model's strongest learned feature (if it's highly predictive, which a "test outcome" column usually is) is being driven by a crude 2-bucket proxy instead of real data.
- If `outcome_variable` is itself strongly correlated with the diagnosis, it may be acting as a near-leak of the target — making the documented accuracy number look better than it would be on a fair, leakage-free feature set.

**Investigation before fixing:**
1. Read `data/schema.md`'s description of what `outcome_variable` actually represents in the source dataset.
2. If your model is a plain `RandomForestClassifier` (not wrapped where introspection is blocked), check `.feature_importances_` — if `outcome_variable` dominates, that confirms the leakage concern.
3. Check `train_model.py` to see whether `outcome_variable` and `risk_level` are in the training `X` matrix today.

**Recommended fix (Plan A — remove the leaky/unobtainable feature):**
Retrain without `outcome_variable` and `risk_level` as inputs. Neither is legitimately available for a brand-new prediction request, so a model that depends on them can't be served honestly regardless of what's substituted at inference time.

```python
# train_model.py — illustrative
FEATURE_COLUMNS = [
    "age", "gender", "fever", "cough", "fatigue",
    "difficulty_breathing", "blood_pressure", "cholesterol_level",
]
X = df[FEATURE_COLUMNS]   # outcome_variable, risk_level intentionally excluded
y = df["disease"]
```

**Plan B (keep the columns):** Not viable for a real "new patient" use case — there is no honest way to populate `outcome_variable` for someone who hasn't been diagnosed yet. Document why Plan B was rejected rather than re-attempting a smarter heuristic.

**Tests to add:**
- Assert the fitted pipeline's expected input columns exclude `outcome_variable` / `risk_level`.
- Re-run the "3–5 known rows from `Cleaned_Dataset.csv`" validation method already described in `plansdaybyday.md` Day 2 / `PRD.md` §15.4, and record the new pass rate.

**Docs to update after fix:** `claude.md` §1.4 gap summary, `PRD.md` §13.1/§21 (Q-005), `data/schema.md` (mark these columns "training-data only, not a model input"), and any externally published accuracy claim.

---

### 🟠 BUG-102 — Redundant double scaling of vitals

**Confirmed issue:** `app.py` builds `age_scaled`, `bp_scaled`, `chol_scaled` via a standalone `scaler.pkl`, then passes **all six** numeric columns (3 raw + 3 pre-scaled) into `best_model.pkl`. That pipeline's internal `ColumnTransformer` scales all six again — so the three "scaled" columns get scaled twice, and the three raw columns get a different scaling treatment than they had at training-time-via-notebook (unless this exact double-pass was also how training was originally run, which needs verifying).

**Root cause:** Two scalers exist where one Pipeline should: an external `scaler.pkl` (added during the Day 2 "skew fix") and an internal `ColumnTransformer` baked into `best_model.pkl` by `train_model.py`. Whichever was added later, the result is statistically redundant features (RandomForest learning split rules on two correlated/duplicated versions of the same signal) on an already-small 349-row dataset — bad for generalization even where it isn't mathematically "wrong."

**Investigation before fixing:**
1. Open `train_model.py` and confirm exactly which columns its `ColumnTransformer` treats as numeric.
2. Confirm whether `Cleaned_Dataset.csv` itself already contains `age_scaled` / `bp_scaled` / `chol_scaled` as pre-existing columns (per `data/schema.md`'s "scaled numeric columns" mention) or whether these are purely runtime-only.
3. Determine whether this 6-column redundancy was present during the *original* training run too (if so, it's "self-consistent but bad architecture"; if not, it's an active skew on top of the redundancy).

**Recommended fix — bundle with BUG-101, retrain once:**
Consolidate to a single `sklearn.Pipeline` that owns all preprocessing. Drop the external `scaler.pkl` entirely.

```python
# train_model.py — illustrative
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

numeric_features = ["age", "blood_pressure", "cholesterol_level"]
passthrough_features = ["gender", "fever", "cough", "fatigue", "difficulty_breathing"]

preprocessor = ColumnTransformer([
    ("scale", StandardScaler(), numeric_features),
    ("pass", "passthrough", passthrough_features),
])

pipeline = Pipeline([
    ("preprocess", preprocessor),
    ("clf", RandomForestClassifier(random_state=42)),
])
pipeline.fit(X_train, y_train)
joblib.dump(pipeline, "best_model.pkl")   # single artifact — no separate scaler.pkl
```

```python
# app.py /predict — illustrative, after fix
input_df = pd.DataFrame([{
    "age": age, "gender": gender, "fever": fever, "cough": cough,
    "fatigue": fatigue, "difficulty_breathing": breathing,
    "blood_pressure": blood_pressure, "cholesterol_level": cholesterol,
}])
probabilities = best_model.predict_proba(input_df)[0]   # scaling happens inside the pipeline now
```
Delete the manual `scaler.transform()` block and the `scaler.pkl` load. Update `config.py` (`SCALER_PATH`) and `.env.example` accordingly if the artifact is removed.

**Tests to add:**
- Assert `input_df` passed into the model contains exactly the expected raw columns (no `_scaled` duplicates).
- A unit test feeding one known raw row through the pipeline and checking the scaled intermediate values match expectation (catches any future re-introduction of double-scaling).

**Docs to update after fix:** `claude.md`'s "Training-Serving Skew: RESOLVED ✅" line needs an honest addendum — the Day 2 fix solved the *external* mismatch but missed this *internal* duplication. Same correction in `PRD.md` §5.4 and §13.2.

> ⚠️ **Sequencing note:** Do BUG-101 and BUG-102 in the same retraining pass — both touch `train_model.py` and regenerate artifacts. Retraining twice wastes effort and risks inconsistent intermediate states.

---

### 🟡 BUG-103 — Model selection (`model` param) is silently ignored

**Confirmed issue:** `app.py` reads `model_choice = data.get('model', 'rf')` and echoes it back as `model_used`, but only `best_model.pkl` (Random Forest) is ever loaded. Requesting `"gb"` or `"lr"` does nothing except produce a misleading response field — and this is actively documented as real in both `README.md` and `api.md`.

**Recommended fix (minimal — be honest, low effort):**
```python
# app.py — illustrative
requested_model = data.get("model", "rf")
actual_model_used = "rf"   # only model currently trained/served
if requested_model != actual_model_used:
    logger.info("Model '%s' requested but unavailable; served with '%s'", requested_model, actual_model_used)
response["model_used"] = actual_model_used   # always reflects what actually ran
```
Update `api.md` / `README.md`: either remove `gb`/`lr` from the documented enum, or explicitly mark them "accepted but not yet implemented — requests fall back to `rf`, and `model_used` reflects the actual model."

**Optional full fix (stretch goal, higher effort):** Extend `train_model.py` to also fit `GradientBoostingClassifier` and `LogisticRegression` on the same (post-BUG-101/102) feature set, serialize each, load all three at startup, and route on `model_choice` with proper fallback for unknown values. Only worth doing if multi-model comparison is a feature you actually want to showcase.

**Tests to add:** A case in `test_predict.py` asserting that requesting `"model": "gb"` returns `model_used == "rf"` (or whatever the honest value is) rather than echoing the request.

---

### 🟡 BUG-104 — Mobile hamburger menu has no JS handler

**Confirmed issue:** `style.css` shows a `.hamburger` button at mobile breakpoints; `main.js` has no click listener wired to it, so the button does nothing.

**Fix:**
```javascript
// main.js — illustrative, adjust selectors to actual markup
const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-links");

hamburger?.addEventListener("click", () => {
  const isOpen = navMenu.classList.toggle("active");
  hamburger.setAttribute("aria-expanded", String(isOpen));
});

navMenu?.querySelectorAll("a").forEach((link) =>
  link.addEventListener("click", () => navMenu.classList.remove("active"))
);
```
Confirm `style.css` has a visible "open" state for `.nav-links.active` at the documented 768px breakpoint — add it if it's missing, not just the JS toggle.

Since `main.js` is shared across `index.html`, `about.html`, and `contact.html` (per `AGENTS.md`), verify the fix works on all three pages, not just the home page.

**Tests:** This is a DOM/JS interaction — manual QA at <768px viewport on all three pages is the practical check (no existing test infra covers JS-only frontend behavior).

---

### 🟢 BUG-105 — Confidence value type mismatch (demo-mode fallback)

**Confirmed issue:** The demo-mode fallback in `main.js` formats confidence via `.toFixed(1)`, which returns a **string**. The live backend returns a **float** via `round(main_confidence, 2)`. Any downstream code doing numeric comparison, sorting, or arithmetic on `confidence` will behave inconsistently depending on whether data came from the API or the fallback.

**Fix:**
```javascript
// Before:
confidence: someValue.toFixed(1)        // string, 1 decimal

// After:
confidence: Number(someValue.toFixed(2)) // number, 2 decimals — matches backend precision
```
Keep formatting (e.g., appending `%`) at the render/display step, not baked into the data object — that's what caused the drift in the first place.

**Tests:** A simple check that both the live-mode and demo-mode code paths produce `typeof confidence === "number"`.

---

### 🟠 BUG-106 — Vacuous assertion in `test_request_logging_avoids_payload_values`

**Confirmed issue:** The test asserts `"30" not in logs`, assuming the fixture's age is `30`. The actual `valid_prediction_data` fixture in `conftest.py` uses `age: 45`. The assertion passes regardless of whether real leakage occurs, because `"30"` was never going to appear either way.

**Fix:**
```python
# tests/test_observability.py — illustrative
def test_request_logging_avoids_payload_values(client, valid_prediction_data, caplog):
    client.post("/predict", json=valid_prediction_data)
    logged_text = caplog.text
    assert str(valid_prediction_data["age"]) not in logged_text
    assert str(valid_prediction_data["gender"]) not in logged_text
```
Better still: parametrize across a couple of distinct payload fixtures (different ages) so a future fixture change can't silently make the test vacuous again the same way.

**Dependency:** This test will *fail* once it's fixed correctly, until BUG-107 is also fixed — do them together.

---

### 🔴 BUG-107 — Real PHI leak: raw age/gender logged in production

**Confirmed issue:** `app.py` contains something like `logger.info("Patient: Age %d, Gender %s", age, ...)`, which puts raw patient-identifying fields into logs. This directly contradicts `AGENTS.md`'s stated rule ("the app should not persist patient inputs") and the explicit "COMPLETED" claims in `audit_report.md` and `PROGRESS_AND_STATUS.md` that PHI is excluded from logs.

**Fix:**
```python
# Before — illustrative:
logger.info("Patient: Age %d, Gender %s", age, gender)

# After — log operational signal only, never raw identifying fields:
logger.info(
    "Prediction served — symptom_count=%d risk=%s top1=%s confidence=%.2f",
    symptom_count, risk_level, top1_disease, confidence,
)
```
**Do a full sweep, not just one line.** Search the whole file for any `logger.*` call that interpolates `age`, `gender`, `blood_pressure`, `cholesterol`, or the symptom flags directly — scrub all of them, not just the one quoted in the bug report.

**Tests:** Fix BUG-106 as shown above, then confirm it fails on current code and passes after this fix. Consider adding a more general test that posts several randomized valid payloads and asserts none of their field *values* appear anywhere in captured log text — more robust than checking one hardcoded field name.

**Docs to correct:** `audit_report.md`'s "Request Timing Logs... COMPLETED" line and `PROGRESS_AND_STATUS.md`'s "ensuring patient-identifying data remains unlogged" line both need an addendum noting this was found and fixed on 2026-06-26 (or whenever you land it).

---

### 🔴 BUG-108 — `/health` always reports `200 healthy`, even when models fail to load

**Confirmed issue:** `api.md` documents that `/health` should return `500` with `status: "degraded"` if critical artifacts fail to load. The actual implementation always returns `200 healthy`, even when `best_model` or `scaler` is `None`.

**Why this matters more than it looks:** Container orchestration (Docker `HEALTHCHECK`, and any future Kubernetes/Cloud Run liveness probe per `architectural_advisory.md`) decides whether to route traffic based on this status code. If `/health` always says "fine," a deployment that's silently missing its model files will pass every health check while every real `/predict` call returns `500`. This is exactly the scenario `observability.md` already flags as a known CI gap (`.pkl` files are gitignored, so the CI-built Docker image has no models) — which means your current "Docker image builds, `/health` returns 200" quality gate may be passing for the wrong reason.

**Fix:**
```python
# app.py — illustrative
@app.route("/health")
def health():
    artifacts = {
        "model_loaded": best_model is not None,
        "encoder_loaded": disease_encoder is not None,
        "scaler_loaded": scaler is not None,            # drop this key if BUG-102 removes scaler.pkl
        "medicine_db_loaded": medicine_db is not None,
    }
    critical_ok = artifacts["model_loaded"] and artifacts["encoder_loaded"]
    status_code = 200 if critical_ok else 503
    return jsonify({
        "status": "healthy" if critical_ok else "degraded",
        **artifacts,
        "message": "Backend is running!" if critical_ok
                    else "Critical dependencies are missing.",
    }), status_code
```
**Decision needed from you:** which artifacts are "critical" (fail health) vs. "optional" (degrade gracefully per the existing fallback-advice behavior). Recommendation: `model` + `encoder` are hard-required; `medicine_db` missing can stay non-fatal since `app.py` already has fallback advice logic for that case.

**Also decide:** `500` (per current `api.md`) vs `503 Service Unavailable` (more semantically correct for "dependency not ready"). Either is fine — just make the code and `api.md` agree.

**Tests to add:** Mock `best_model = None` at app context level, hit `/health`, assert non-200 status code and `status: "degraded"` in the body. Your current test suite almost certainly doesn't have this case — add it.

**Docs to correct:** `audit_report.md`'s "Expand /health: COMPLETED" claim should be amended — adding the boolean flags was done correctly; the status-code/degraded-state semantics were not, until this fix lands. Update `api.md` to match whichever status code you choose.

---

## 4. Recommended Execution Roadmap

### Phase A — Immediate Quick Wins (no retraining, ~1 day)
Do these first — low effort, several are CRITICAL severity, and none depend on the bigger ML rework.

| Order | Task | Bugs |
|---|---|---|
| 1 | Fix the vacuous test, then fix the real PHI log leak it should have caught | BUG-106 → BUG-107 |
| 2 | Fix `/health` to honestly report degraded state | BUG-108 |
| 3 | Make `model_used` honest in API responses | BUG-103 (minimal) |
| 4 | Wire up the mobile hamburger menu | BUG-104 |
| 5 | Fix confidence type mismatch in demo-mode fallback | BUG-105 |

### Phase B — ML Pipeline Correctness Overhaul (requires retrain, ~3–5 days)
Higher effort, needs a couple of design decisions up front (see investigation steps in §3).

| Order | Task | Bugs |
|---|---|---|
| 1 | Confirm root causes against live `train_model.py` / `Cleaned_Dataset.csv` | BUG-101, BUG-102 |
| 2 | Redesign `train_model.py` into a single consolidated Pipeline; drop leaky/unobtainable features | BUG-101, BUG-102 |
| 3 | Retrain once, regenerate `best_model.pkl` / `disease_encoder.pkl`; retire `scaler.pkl` if consolidated | BUG-101, BUG-102 |
| 4 | Simplify `app.py`'s `/predict` accordingly | BUG-101, BUG-102 |
| 5 | Re-run the 3–5 known-row validation from `PRD.md` §15.4; record honest accuracy | BUG-101, BUG-102 |
| 6 | Update `conftest.py` mock fixtures to match the new pipeline shape; update/extend tests | BUG-101, BUG-102 |

### Phase C — Documentation & Quality Gate Sync (~0.5–1 day)
Do last, once Phases A and B are verified.

- Correct the specific lines flagged in §0 and within each bug section above (`claude.md`, `PRD.md`, `audit_report.md`, `quality_gates.md`, `PROGRESS_AND_STATUS.md`, `api.md`, `data/schema.md`).
- Re-run `ruff check .` and `pytest --cov-fail-under=80`; confirm coverage gate still holds after test changes.
- Re-publish any externally stated accuracy number only after Phase B's honest re-validation.
- Optional stretch: use BUG-108 as the forcing function to finally implement the model-artifact-fetching strategy for CI that `observability.md` already flags as unresolved.

---

## 5. New Technical Debt Register Entries

Append these to the technical debt register in `claude.md` / `PRD.md` §19.1:

| ID | Location | Description | Priority | Status |
|---|---|---|---|---|
| TD-006 | `app.py` (`/predict`) | `outcome_variable` synthesized via heuristic instead of using a non-leaky feature set | CRITICAL | Open |
| TD-007 | `app.py` + `train_model.py` | Numeric vitals scaled twice (external `scaler.pkl` + internal `ColumnTransformer`) | HIGH | Open |
| TD-008 | `app.py` (`/predict`) | `model` request param accepted but never honored | MEDIUM | Open |
| TD-009 | `static/js/main.js` | Hamburger menu has no event listener | MEDIUM | Open |
| TD-010 | `static/js/main.js` | Demo-mode confidence values typed as string, not number | LOW | Open |
| TD-011 | `tests/test_observability.py` | PHI-leakage test asserts against a literal that doesn't match the fixture | HIGH | Open |
| TD-012 | `app.py` | Raw patient age/gender logged via `logger.info` | CRITICAL | Open |
| TD-013 | `app.py` (`/health`) | Always returns `200 healthy` regardless of artifact load state | CRITICAL | Open |

---

## 6. Quality Gate Additions

Add these checks to `quality_gates.md`:

- [ ] No request-payload field values (age, gender, blood pressure, cholesterol, symptom flags) appear in captured log output across multiple distinct test payloads
- [ ] `/health` returns a non-200 status and `status: "degraded"` when `best_model` or `disease_encoder` is `None`
- [ ] `model_used` in `/predict` responses always reflects the model that actually ran, never the raw client-requested value
- [ ] Model's expected input feature set excludes any column not legitimately available for a new, undiagnosed patient
- [ ] Mobile nav (`.hamburger`) toggles visibly at <768px on `index.html`, `about.html`, and `contact.html`

---

## 7. Documentation Correction Checklist

| Doc | Section | Correction needed |
|---|---|---|
| `claude.md` | §1.4 Gap Summary | Amend "Training-serving skew: None" — note the internal double-scaling/leakage finding and resolution date |
| `PRD.md` | §5.4, §13.2, §21 (Q-005) | Same correction; revisit Q-005's "RESOLVED" status |
| `audit_report.md` | Request Timing Logs row; Expand /health row | Amend both "COMPLETED" claims with the PHI-leak and degraded-state findings |
| `PROGRESS_AND_STATUS.md` | Day 9 section | Amend "patient-identifying data remains unlogged" claim |
| `quality_gates.md` | Data Quality Gates | Add the new checks from §6 above |
| `api.md` | `/health` section | Sync documented status code (500 vs 503) with whatever you implement |
| `api.md`, `README.md` | `/predict` request schema | Either remove `gb`/`lr` from the model enum or mark them "not yet implemented" |
| `data/schema.md` | Column descriptions | Mark `outcome_variable` / `risk_level` as training-data-only if Phase B removes them as model inputs |

---

## 8. Final Verification Protocol

Run this after each phase, not just at the end:

```powershell
# Lint
.\venv\Scripts\python.exe -m ruff check .

# Tests + coverage
.\venv\Scripts\python.exe -m pytest --cov-fail-under=80 --cov-report=term-missing

# Manual smoke checks
curl.exe http://localhost:5000/health
curl.exe -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d "{...}"

# After Phase B retrain specifically: re-run the 3-5 known-row validation
# from Cleaned_Dataset.csv against /predict and record actual vs predicted disease
```

Don't consider any bug "closed" until: the fix is in, a test specifically targets the failure mode (not just exercises the code path), and the relevant doc claim is corrected.
