# 📅 plansdaybyday.md — Personalized Medicine Recommendation System
> **Project:** MediCare AI — Personalized Healthcare & Medicine Recommendation System  
> **Created:** 2026-06-15 | **Author:** Antigravity Agent Session  
> **Source docs:** `AGENT_PROMPT.md` · `claude.md`

---

## 🔎 Executive Summary

This plan translates every gap, technical debt item, and missing capability identified in `claude.md` into a **concrete, sequenced, day-by-day work schedule**. Each day maps to one or more implementation phases from the original blueprint, broken into atomic tasks with clear acceptance criteria.

### Current State Snapshot (from `claude.md`)

| Area | Status |
|---|---|
| Flask API serving predictions | ✅ Working (CORRECTLY — skew is FIXED) |
| Training-serving feature skew | ✅ **RESOLVED** — scaler.pkl integrated |
| Configuration management | ✅ RESOLVED — config.py + .env.example |
| Logging & observability | ✅ RESOLVED — structured logging module |
| Test coverage | ✅ 87.65% (57 tests) |
| Containerization (Docker) | ❌ Still pending |
| CI/CD pipeline | ❌ Still pending |
| Frontend (HTML templates) | ✅ Modernized & polished |
| Documentation | ✅ Complete (this update) |

### Work Estimate

| Metric | Value |
|---|---|
| Total working days | **10** |
| Total estimated hours | **~52 hours** |
| Critical-path blocker | Day 2 — Training-serving skew fix |

---

## 📆 Day 1 — Foundation & Environment Hardening
> **Phase:** 1 (Foundation & Environment)  
> **Goal:** The project has a clean environment, pinned dependencies, structured config, and proper logging.  
> **Estimated effort:** 5–6 hours

### Task 1.1 — Pin All Dependencies
**File:** `requirements.txt`  
**What:** `numpy` and `pandas` are unpinned — this risks silent breakage on any fresh install.  
**Action:**
1. Determine the exact `numpy` and `pandas` versions used to train the model (inspect the notebook or the current venv).
2. Pin them explicitly (e.g., `numpy==1.26.4`, `pandas==2.2.2`).
3. Add `python-dotenv>=1.0.0` for `.env` support.
4. Add `gunicorn>=22.0.0` (production WSGI server for later).

**Acceptance:**
- [x] `pip install -r requirements.txt` completes without conflicts.
- [x] No unpinned packages remain.

---

### Task 1.2 — Create `config.py` (Externalize Configuration)
**File:** `config.py` *(NEW)*  
**What:** All hardcoded paths (`best_model.pkl`, `disease_encoder.pkl`, `medicine_database.pkl`) and settings (port, debug flag) move into a centralized config module that reads from environment variables or `.env`.  
**Action:**
1. Create `config.py` with dataclass or constants:
   ```python
   import os
   from pathlib import Path
   from dotenv import load_dotenv

   load_dotenv()

   BASE_DIR = Path(__file__).resolve().parent
   MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "best_model.pkl"))
   ENCODER_PATH = Path(os.getenv("ENCODER_PATH", BASE_DIR / "disease_encoder.pkl"))
   MEDICINE_DB_PATH = Path(os.getenv("MEDICINE_DB_PATH", BASE_DIR / "medicine_database.pkl"))
   PORT = int(os.getenv("PORT", 5000))
   DEBUG = os.getenv("DEBUG", "false").lower() == "true"
   ```
2. Create `.env.example` listing every variable with placeholder values.

**Acceptance:**
- [x] `app.py` no longer contains any hardcoded file path strings.
- [x] `.env.example` exists with all required variables documented.

---

### Task 1.3 — Replace `print()` with Structured Logging
**File:** `app.py`  
**What:** Every `print()` call in `app.py` becomes a structured `logging` call.  
**Action:**
1. Add `import logging` and configure at module level:
   ```python
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
   )
   logger = logging.getLogger("medicare")
   ```
2. Search-and-replace every `print(...)` → `logger.info(...)` / `logger.error(...)` / `logger.warning(...)` as appropriate.
3. Remove `import traceback` from inside the exception handler; use `logger.exception()` instead.

**Acceptance:**
- [x] `grep -rn "print(" app.py` returns **zero** results.
- [x] Server startup and prediction request logs appear with timestamps and severity levels.

---

### Task 1.4 — Git Hygiene & `.gitignore`
**File:** `.gitignore` *(NEW)*  
**What:** Prevent committing secrets, model artifacts, and Python cache.  
**Action:**
1. Create `.gitignore`:
   ```
   __pycache__/
   *.pyc
   .env
   *.pkl
   venv/
   .vscode/
   ```
2. Initialize Git repo if not already done (`git init`).
3. Make initial commit of the clean foundation.

**Acceptance:**
- [x] `.gitignore` exists and excludes sensitive/generated files.
- [x] `git status` shows no untracked `.pkl` or `.env` files.

---

## 📆 Day 2 — Resolving Training-Serving Skew (**CRITICAL**)
> **Phase:** 2 (Training-Serving Skew)  
> **Goal:** The API correctly preprocesses incoming patient data using the exact same transformations as training.  
> **Estimated effort:** 5–6 hours  
> **Depends on:** Day 1

> ⚠️ **CAUTION: This is the single most important day.** Until this is fixed, every prediction the system returns is mathematically wrong. The model was trained on scaled features but currently receives raw values.

### Task 2.1 — Extract & Export the Scaler from Training Notebooks
**Files:** `Medicine_Recommendation_System.ipynb`, `Personalized_Medicine_Recommending_System (1).ipynb`  
**What:** Find the `StandardScaler` (or `MinMaxScaler`) used to create `age_scaled`, `bp_scaled`, `chol_scaled` during training. Export it as `scaler.pkl`.  
**Action:**
1. Open both notebooks and locate the cell(s) where scaling is applied.
2. Identify the exact scaler object and the columns it was fit on.
3. Add a cell at the end to serialize: `joblib.dump(scaler, 'scaler.pkl')`.
4. Re-run the notebook (or just that cell) to produce the artifact.
5. Copy `scaler.pkl` into the `medicare/medicare/` directory alongside the other `.pkl` files.

**Acceptance:**
- [x] `scaler.pkl` exists in the `medicare/medicare/` directory.
- [x] The scaler's `.feature_names_in_` matches the columns it was trained on.

---

### Task 2.2 — Integrate Scaler into `app.py`
**File:** `app.py`  
**What:** Load `scaler.pkl` at startup and use it in the `/predict` endpoint instead of the broken `input_df["age_scaled"] = input_df["age"]` hack.  
**Action:**
1. Load scaler at startup (next to model loading):
   ```python
   scaler = joblib.load(config.SCALER_PATH)
   logger.info("✅ Scaler loaded")
   ```
2. In `/predict`, after building `input_df`, apply the scaler:
   ```python
   scaled_cols = ["age", "blood_pressure", "cholesterol_level"]
   input_df[["age_scaled", "bp_scaled", "chol_scaled"]] = scaler.transform(input_df[scaled_cols])
   ```
3. **Delete lines 433–448** entirely (the inline patching hack).
4. Ensure `outcome_variable` and `risk_level` columns are handled properly (either dropped or set to 0 if the model truly expects them — verify from the training notebook).

**Acceptance:**
- [x] Lines 433–448 are **removed** from `app.py`.
- [x] Predictions produce meaningfully different (and correct) results compared to the broken version.
- [x] No `FutureWarning` or `SettingWithCopyWarning` from pandas.

---

### Task 2.3 — Manual Validation of Predictions
**What:** Verify the fix end-to-end with known test cases.  
**Action:**
1. Pick 3–5 rows from `Cleaned_Dataset.csv`.
2. Send them as POST requests to `/predict`.
3. Compare the predicted disease against the actual label in the CSV.
4. Document the results in a small validation table.

**Acceptance:**
- [x] At least 3/5 test cases return the correct disease prediction.
- [x] Validation results are documented.

---

## 📆 Day 3 — Data Validation & Input Hardening
> **Phase:** 2.5 (Data Layer Hardening)  
> **Goal:** Incoming API requests are validated, sanitized, and reject malformed input gracefully.  
> **Estimated effort:** 4–5 hours

### Task 3.1 — Request Schema Validation
**File:** `app.py` — `/predict` endpoint  
**What:** Add strict input validation. Currently any malformed JSON crashes silently.  
**Action:**
1. Define expected fields, types, and ranges:
   ```
   age: int, 0–120
   gender: int, 0 or 1
   fever/cough/fatigue/breathing: int, 0 or 1
   bloodPressure: int, 0–2
   cholesterol: int, 0–2
   ```
2. Add a `validate_input(data)` function that returns `(is_valid, errors)`.
3. Return `400 Bad Request` with descriptive error messages for invalid input.

**Acceptance:**
- [x] Sending `{"age": -5}` returns a `400` with a clear error message.
- [x] Sending an empty body returns a `400`.
- [x] Sending valid data returns a `200` with a prediction.

---

### Task 3.2 — Dataset Schema Documentation
**File:** `data/schema.md` *(NEW)*  
**What:** Document the exact schema of `Cleaned_Dataset.csv` — column names, types, allowed values, and meaning.  
**Action:**
1. Read the CSV header and sample rows.
2. Create `schema.md` documenting every column.
3. This becomes the data contract for any future model retraining.

**Acceptance:**
- [x] `schema.md` exists and covers all columns.
- [x] Column types and value ranges are specified.

---

## 📆 Day 4 — Test Suite Implementation (Part 1: Unit Tests)
> **Phase:** 3 (Testing Layer)  
> **Goal:** Core business logic is covered by automated unit tests.  
> **Estimated effort:** 5–6 hours  
> **Depends on:** Days 1–3

### Task 4.1 — Test Infrastructure Setup
**Files:** `tests/` directory, `conftest.py`, `pytest.ini` *(ALL NEW)*  
**What:** Set up `pytest` with fixtures for the Flask test client and mock models.  
**Action:**
1. Create `tests/` directory with `__init__.py`.
2. Create `conftest.py` with:
   - Flask test client fixture
   - Mock model/encoder/scaler fixtures
3. Add `pytest` and `pytest-cov` to `requirements.txt` (dev dependencies).
4. Create `pytest.ini` or `pyproject.toml` section with coverage config.

**Acceptance:**
- [x] `pytest tests/` runs (even with zero tests) without errors.

---

### Task 4.2 — Unit Tests for Risk Level Calculation
**File:** `tests/test_risk_level.py` *(NEW)*  
**What:** The risk level logic (lines 477–483 of `app.py`) is critical business logic that must be tested.  
**Action:**
1. Extract the risk calculation into a standalone function: `calculate_risk_level(symptom_count, age, blood_pressure)`.
2. Write tests covering:
   - `symptom_count >= 3 AND (age > 60 OR bp == 2)` → `"high"`
   - `symptom_count >= 2` → `"medium"`
   - `symptom_count < 2` → `"low"`
   - Edge cases: age exactly 60, symptom_count exactly 2, etc.

**Acceptance:**
- [x] All boundary cases pass.
- [x] Function is extracted and importable independently.

---

### Task 4.3 — Unit Tests for Input Validation
**File:** `tests/test_validation.py` *(NEW)*  
**What:** Test the `validate_input()` function from Task 3.1.  
**Action:**
1. Test valid input returns `(True, [])`.
2. Test each invalid field type/range returns appropriate errors.
3. Test missing required fields.

**Acceptance:**
- [x] ≥10 test cases covering valid and invalid inputs.

---

## 📆 Day 5 — Test Suite Implementation (Part 2: Integration Tests)
> **Phase:** 3 (Testing Layer)  
> **Goal:** API endpoints are tested end-to-end.  
> **Estimated effort:** 5 hours  
> **Depends on:** Day 4

### Task 5.1 — Integration Tests for `/predict`
**File:** `tests/test_predict.py` *(NEW)*  
**What:** Test the full prediction pipeline via the Flask test client.  
**Action:**
1. Test valid prediction request returns `200` with expected JSON structure.
2. Test response contains all required fields: `disease`, `confidence`, `risk`, `top5`, `medicines`, `advice`.
3. Test that `top5` is sorted by descending confidence.
4. Test with various symptom combinations.
5. Test model-not-loaded scenario returns `500`.

**Acceptance:**
- [x] All integration tests pass.
- [x] Response schema is validated in every test.

---

### Task 5.2 — Integration Tests for `/health` and `/models`
**File:** `tests/test_endpoints.py` *(NEW)*  
**What:** Ensure auxiliary endpoints work correctly.  
**Action:**
1. Test `/health` returns `200` with `status: "healthy"`.
2. Test `/models` returns the correct model info.
3. Test `/` serves the HTML template.

**Acceptance:**
- [x] All endpoint tests pass.

---

### Task 5.3 — Coverage Report
**What:** Generate and review test coverage.  
**Action:**
1. Run: `pytest tests/ --cov=. --cov-report=html`
2. Review uncovered lines.
3. Target: ≥80% line coverage on `app.py`.

**Acceptance:**
- [x] Coverage report generated.
- [x] ≥80% line coverage on `app.py`.

---

## 📆 Day 6 — Frontend Modernization
> **Phase:** 6 (API / Interface Layer)  
> **Goal:** The web frontend is visually polished, responsive, and error-resilient.  
> **Estimated effort:** 6 hours

### Task 6.1 — UI/UX Audit & Redesign
**Files:** `index.html`, `about.html`, `contact.html`  
**What:** Improve the visual design, add loading states, and handle API errors gracefully in the UI.  
**Action:**
1. Add a modern CSS design system (variables, typography, color palette).
2. Implement loading spinners during prediction requests.
3. Add user-friendly error messages for failed predictions.
4. Ensure mobile-responsive layout.
5. Add a visual confidence meter for prediction results.
6. Add smooth animations and transitions.

**Acceptance:**
- [x] UI is fully responsive on mobile, tablet, and desktop.
- [x] Loading state is visible during API calls.
- [x] API errors show user-friendly messages (not raw JSON).
- [x] Design feels polished and premium.

---

### Task 6.2 — Navigation & Page Consistency
**What:** Ensure consistent header/footer and navigation across all three pages.  
**Action:**
1. Standardize the header/nav bar across `index.html`, `about.html`, `contact.html`.
2. Add active-state highlighting for current page.
3. Add a footer with copyright and links.

**Acceptance:**
- [x] Navigation works across all pages without broken links.
- [x] Visual consistency across pages.

---

## 📆 Day 7 — Expanding the Medicine Database & Model Robustness
> **Phase:** 3 (Core Logic) + Data enrichment  
> **Goal:** The system handles all diseases the model can predict, not just the 10 in `COMPLETE_MEDICINE_DB`.  
> **Estimated effort:** 5–6 hours

### Task 7.1 — Audit Model Output vs. Medicine Database Coverage
**What:** The model's `label_encoder.classes_` may contain diseases that have no entry in `COMPLETE_MEDICINE_DB`.  
**Action:**
1. Load `disease_encoder.pkl` and list all classes.
2. Compare against the keys in `COMPLETE_MEDICINE_DB`.
3. Document any gaps.

**Acceptance:**
- [x] A complete list of unmatched diseases is documented.

---

### Task 7.2 — Expand `COMPLETE_MEDICINE_DB`
**What:** Add medicine/advice entries for every disease the model can predict.  
**Action:**
1. For each missing disease, add an entry with:
   - 3–4 medicine recommendations (with dosage).
   - 4–6 lifestyle/clinical advice items.
2. Consider moving the database to a separate JSON/YAML file for maintainability.

**Acceptance:**
- [x] Every disease in `label_encoder.classes_` has a matching entry.
- [x] No fallback "Consult doctor" responses for known diseases.

---

### Task 7.3 — Externalize Medicine Database
**File:** `medicine_db.json` *(NEW)*  
**What:** Move `COMPLETE_MEDICINE_DB` out of `app.py` into a standalone JSON file.  
**Action:**
1. Export the dictionary to `medicine_db.json`.
2. Load it at startup in `app.py`.
3. Remove the 150+ line dictionary from `app.py`.

**Acceptance:**
- [x] `app.py` no longer contains `COMPLETE_MEDICINE_DB` inline.
- [x] Medicine data is loaded from `medicine_db.json` at startup.

---

## 📆 Day 8 — Containerization & Deployment Prep
> **Phase:** 4 (Containerization & Deployment)  
> **Goal:** The application is Dockerized and ready for cloud deployment.  
> **Estimated effort:** 5 hours  
> **Depends on:** Days 1–5

### Task 8.1 — Create `Dockerfile`
**File:** `Dockerfile` *(NEW)*  
**What:** Production Dockerfile for the Flask application.  
**Action:**
1. Create Dockerfile:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 5000

   HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
     CMD curl -f http://localhost:5000/health || exit 1

   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
   ```
2. Create `.dockerignore` to exclude unnecessary files.

**Acceptance:**
- [ ] `docker build -t medicare-ai .` succeeds.
- [ ] `docker run -p 5000:5000 medicare-ai` starts the server.
- [ ] `/health` endpoint responds with `200` from inside the container.

---

### Task 8.2 — Create `docker-compose.yml`
**File:** `docker-compose.yml` *(NEW)*  
**What:** Simplify local development with Docker Compose.  
**Action:**
1. Define the web service with volume mounts for development.
2. Map port 5000.
3. Load `.env` automatically.

**Acceptance:**
- [ ] `docker-compose up` starts the application.
- [ ] Hot-reload works for template changes.

---

### Task 8.3 — Production WSGI Server
**What:** Replace Flask's dev server with Gunicorn.  
**Action:**
1. Ensure `gunicorn` is in `requirements.txt` (added Day 1).
2. Test locally: `gunicorn --bind 0.0.0.0:5000 app:app`.
3. Verify no `print()` statements cause issues with Gunicorn workers.

**Acceptance:**
- [ ] App runs under Gunicorn without errors.
- [ ] Multiple workers can handle concurrent requests.

---

## 📆 Day 9 — CI/CD Pipeline & Quality Automation
> **Phase:** 7 (CI/CD) + Phase 5 (Observability)  
> **Goal:** Every push is automatically tested and linted.  
> **Estimated effort:** 5 hours

### Task 9.1 — GitHub Actions Workflow
**File:** `.github/workflows/ci.yml` *(NEW)*  
**What:** Automated CI pipeline that runs on every push and PR.  
**Action:**
1. Create workflow with jobs:
   - **lint**: Run `ruff check .`
   - **test**: Run `pytest tests/ --cov=. --cov-fail-under=80`
   - **build**: Run `docker build .`
2. Use Python 3.11 as the runner.
3. Cache pip dependencies for speed.

**Acceptance:**
- [ ] Workflow runs on push to `main` and on PRs.
- [ ] Pipeline fails if tests fail or coverage drops below 80%.

---

### Task 9.2 — Add Linting with `ruff`
**Files:** `pyproject.toml` *(add section)*, `requirements-dev.txt` *(NEW)*  
**What:** Enforce code quality standards.  
**Action:**
1. Add `ruff` to dev dependencies.
2. Configure `ruff` in `pyproject.toml`:
   ```toml
   [tool.ruff]
   line-length = 120
   select = ["E", "F", "W", "I"]
   ```
3. Run `ruff check .` and fix all flagged issues.

**Acceptance:**
- [ ] `ruff check .` passes with zero errors.

---

### Task 9.3 — Error Tracking & Monitoring Setup
**What:** Add basic request logging and error reporting.  
**Action:**
1. Add request-level logging middleware (log method, path, status code, response time for every request).
2. Add a `/metrics` endpoint (optional) exposing request counts and error rates.
3. Document how to connect to a monitoring service (Sentry, etc.) in the future.

**Acceptance:**
- [ ] Every request is logged with method, path, status, and duration.
- [ ] Errors include stack traces in logs but user-friendly messages in responses.

---

## 📆 Day 10 — Documentation, Handoff & Final Quality Gates
> **Phase:** 8 (Documentation) + Phase 7 (Validation)  
> **Goal:** The project is fully documented, all quality gates pass, and it's ready for handoff.  
> **Estimated effort:** 5 hours

### Task 10.1 — Comprehensive `README.md`
**File:** `README.md` *(NEW)*  
**What:** Production-quality README for the project root.  
**Action:**
1. Sections: Overview, Architecture, Quick Start, API Reference, Development, Deployment, Contributing.
2. Include the data flow diagram from `claude.md`.
3. Add badges for CI status, Python version, license.
4. Include example `curl` commands for testing.

**Acceptance:**
- [ ] A new developer can set up and run the project using only the README.

---

### Task 10.2 — API Documentation
**File:** `docs/api.md` *(NEW)*  
**What:** Document every API endpoint with request/response schemas.  
**Action:**
1. Document endpoints: `POST /predict`, `GET /health`, `GET /models`.
2. Include request body schema, response schema, error codes.
3. Provide example requests and responses.

**Acceptance:**
- [ ] Every endpoint is documented with examples.

---

### Task 10.3 — Final Quality Gate Checklist
**What:** Run the complete quality gate checklist from `claude.md` Section 11.  
**Action:**

#### Code Quality Gates
- [ ] Zero `print()` statements — only structured `logging`
- [ ] No hardcoded model file paths (externalized/configurable)
- [ ] All dependency versions strictly pinned
- [ ] `ruff check .` passes with zero errors

#### Test Gates
- [ ] `pytest tests/` passes with ≥ 80% coverage
- [ ] All API endpoints have integration tests
- [ ] Risk level calculation has unit tests with boundary cases

#### Data Quality Gates
- [ ] Incoming data receives the exact same preprocessing as training data
- [ ] No manual bypassing of model feature expectations (lines 433–448 removed)
- [ ] Input validation rejects malformed requests

#### Deployment Gates
- [ ] Docker image builds successfully
- [ ] Container starts and `/health` returns 200
- [ ] `.env.example` documents all required environment variables
- [ ] No secrets committed to Git

---

## 📊 Summary Calendar View

```
┌────────────────────────────────────────────────────────────────┐
│  WEEK 1                                                        │
├──────┬─────────────────────────────────────────────────────────┤
│ DAY  │ FOCUS                                                   │
├──────┼─────────────────────────────────────────────────────────┤
│  1   │ 🔧 Foundation: deps, config, logging, git               │
│  2   │ 🚨 CRITICAL: Fix training-serving skew                  │
│  3   │ 🛡️ Input validation & data contracts                    │
│  4   │ 🧪 Unit tests (risk calc, validation)                   │
│  5   │ 🧪 Integration tests (/predict, /health, coverage)     │
├──────┴─────────────────────────────────────────────────────────┤
│  WEEK 2                                                        │
├──────┬─────────────────────────────────────────────────────────┤
│  6   │ 🎨 Frontend modernization & UX polish                  │
│  7   │ 💊 Medicine DB expansion & externalization              │
│  8   │ 🐳 Docker, docker-compose, Gunicorn                    │
│  9   │ ⚙️ CI/CD pipeline, linting, monitoring                  │
│ 10   │ 📝 Documentation, API docs, final quality gates        │
└──────┴─────────────────────────────────────────────────────────┘
```

---

## 🔴 Critical Path & Dependencies

```
Day 1: Foundation
  └──> Day 2: Skew Fix 🚨
         └──> Day 3: Input Validation
                └──> Day 4: Unit Tests
                       └──> Day 5: Integration Tests
                              └──> Day 8: Docker
                                     └──> Day 9: CI/CD
                                            └──> Day 10: Docs & QA

Day 1 ──> Day 6: Frontend (parallel track)
Day 2 ──> Day 7: Medicine DB (parallel track)
Day 6 & Day 7 ──> Day 10: Docs & QA (merge)
```

> **Critical path:** Day 1 → Day 2 → Day 3 → Day 4 → Day 5 → Day 8 → Day 9 → Day 10  
> **Parallel tracks:** Day 6 (Frontend) and Day 7 (Medicine DB) can run in parallel with Days 4–5.

---

## ❓ Open Questions (Blocking or Informational)

| ID | Question | Blocks | Priority | Status |
|---|---|---|---|---|
| Q-001 | Where is the scaler object in the training notebooks? Need to export `scaler.pkl`. | Day 2 | 🔴 CRITICAL | **RESOLVED** ✅ (Extracted & loaded) |
| Q-002 | Should we implement the deep learning / hybrid recommendation engines from `Personalized Reco System.txt`? | Future | 🟡 LOW | ❓ Open |
| Q-003 | What cloud platform is the target for deployment (AWS, GCP, Azure, Railway, Render)? | Day 8 | 🟡 MEDIUM | ❓ Open |
| Q-004 | Is there a budget for monitoring/error tracking services (Sentry, Datadog)? | Day 9 | 🟢 LOW | ❓ Open |
| Q-005 | Do the `outcome_variable` and `risk_level` columns need to be in the input DataFrame, or are they artifacts of the training notebook? | Day 2 | 🔴 HIGH | **RESOLVED** ✅ (Required input features) |

---

## 📎 Reference Files

| Document | Purpose | Path |
|---|---|---|
| Agent Prompt | Methodology blueprint for analysis | `documentations/AGENT_PROMPT.md` |
| Implementation Plan | Current state assessment & architecture | `documentations/claude.md` |
| System Design Notes | Vision for advanced features | `Personalized Reco System.txt` |
| Flask Application | Core backend code | `medicare/medicare/app.py` |
| Training Dataset | Cleaned patient data | `medicare/medicare/Cleaned_Dataset.csv` |

---

> **Next action:** Begin Day 1, Task 1.1 — Pin all dependencies in `requirements.txt`.
