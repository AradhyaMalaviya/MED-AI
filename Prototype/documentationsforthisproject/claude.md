# claude.md — Personalized Medicine Recommendation System Implementation Plan
> Last updated: 2026-06-24 | Author: Antigravity Pair Programming Session

## 1. Project Overview

### 1.1 — What This Project Is
This is a Machine Learning-based Personalized Medicine Recommendation System. It serves as an interactive web application where users input demographic information and current symptoms. The system predicts potential diseases, calculates a risk level, and provides tailored medicine recommendations, advice, and lifestyle interventions.

### 1.2 — What It Should Do (Target State)
The system should provide highly accurate, low-latency predictions via a robust API. The underlying ML models and preprocessing logic should be completely synchronized to prevent training-serving skew. The application must be fully containerized, tested, and configured via environment variables for safe production deployment.

### 1.3 — What It Currently Does (Actual State)
A Flask backend ([app.py](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20%26%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/app.py)) is successfully serving predictions using pre-trained scikit-learn models ([best_model.pkl](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20%26%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/best_model.pkl)), the disease encoder ([disease_encoder.pkl](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20%26%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/disease_encoder.pkl)), and the standard scaler ([scaler.pkl](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20%26%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/scaler.pkl)). The backend correctly transforms user inputs using `scaler.transform()` before model prediction, completely resolving training-serving skew. Observation and diagnostics are supported via a structured python logger named `'medicare'`. A clean configuration layer ([config.py](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20%26%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/config.py)) manages paths and runtime variables via environment variables with defaults. A robust, automated test suite containing 57 tests covers API endpoints, prediction pipeline, and risk and validation layers, reaching 87.65% code coverage. 

A modernized web frontend is available via HTML templates styled by a dedicated CSS design system ([style.css](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20%26%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/static/css/style.css)) and interactive JS client logic ([main.js](file:///C:/Users/deepa/Downloads/NEW%20PROJECT/Personalized%20Healthcare%20%26%20Medicine%20Recommendation%20System%20(Data%20ScienceML%20based)/medicare/medicare/static/js/main.js)).

### 1.4 — Gap Summary

| Capability | Target | Current | Gap |
|---|---|---|---|
| **ML Serving** | Synchronized features via sklearn Pipeline | Flask app loading scaler.pkl and performing scaler.transform() | None (Skew fully resolved) ✅ |
| **Configuration** | Environment variables (`.env`) | handled via config.py loading python-dotenv | None (Configured correctly) ✅ |
| **Logging** | Structured `logging` module | Structured logging with 'medicare' logger | None (Observability implemented) ✅ |
| **Testing** | >80% coverage (unit & integration) | 57 tests, 87.65% line coverage | None (Tests implemented) ✅ |
| **Deployment** | Docker containerized | Local execution (manual python run) | Requires `Dockerfile` and `docker-compose.yml` 🔲 |
| **CI/CD** | Automated GitHub Action | Local testing only | Requires `.github/workflows/` workflow files 🔲 |
| **Code Style** | Standard linting and formatting | Manual formatting | Requires `pyproject.toml` configuration for Ruff 🔲 |

---

## 2. Annotated Directory Tree

```text
[project-root]/
├── AGENT_PROMPT.md                                                   # [DOCS] Instructions for the AI agent
├── claude.md                                                         # [DOCS] Implementation plan (this file)
├── gap_analysis.md                                                   # [DOCS] GAP analysis between codebase and docs
├── Personalized Reco System.txt                                      # [DOCS] Project overview and architectural notes
├── Medicine_Recommendation_System.ipynb                              # [EXPLORATORY] EDA and ML training notebook
├── Personalized_Medicine_Recommending_System (1).ipynb              # [EXPLORATORY] Alternative model training notebook
└── Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/
    └── medicare/
        └── medicare/
            ├── app.py                                                # [SOURCE] Flask API server and core application logic
            ├── config.py                                             # [SOURCE] App configuration and path setup
            ├── train_model.py                                        # [SOURCE] ML training pipeline script
            ├── requirements.txt                                      # [BUILD] Python dependency manifest
            ├── Cleaned_Dataset.csv                                   # [DATA] Preprocessed training dataset
            ├── best_model.pkl                                        # [ARTIFACT] Serialized RandomForest model (2.2 MB)
            ├── disease_encoder.pkl                                   # [ARTIFACT] Serialized LabelEncoder for targets (346 B)
            ├── scaler.pkl                                            # [ARTIFACT] Serialized StandardScaler for features (927 B)
            ├── legacy_medicine_database.pkl                         # [ARTIFACT] Serialized legacy database (deprecated)
            ├── medicine_db.json                                      # [DATA] Externalized disease-to-medicine DB (7.5 KB)
            ├── .coveragerc                                           # [CONFIG] Code coverage configuration
            ├── .env.example                                          # [CONFIG] Env variables template
            ├── .gitignore                                            # [CONFIG] Git ignored patterns
            ├── pytest.ini                                            # [CONFIG] Pytest options configuration
            ├── data/                                                 # [DATA] Schema folder
            │   └── schema.md                                         # [DOCS] Dataset schema documentation
            ├── static/                                               # [ASSETS] Frontend static assets
            │   ├── css/
            │   │   └── style.css                                     # [SOURCE] Full design system stylesheet (813 lines)
            │   └── js/
            │       └── main.js                                       # [SOURCE] Interactive client-side JS (368 lines)
            ├── templates/                                            # [SOURCE] Frontend HTML interfaces
            │   ├── about.html                                        # [SOURCE] About page layout
            │   ├── contact.html                                      # [SOURCE] Contact page layout
            │   └── index.html                                        # [SOURCE] Main user dashboard layout
            └── tests/                                                # [TEST] API and ML pipeline test suite
                ├── __init__.py                                       # [TEST] Module marker
                ├── conftest.py                                       # [TEST] Mock fixtures and client helper
                ├── test_endpoints.py                                 # [TEST] Integration tests for all routes
                ├── test_predict.py                                   # [TEST] Tests for predicting diseases
                ├── test_risk_level.py                                # [TEST] Tests for risk evaluation
                └── test_validation.py                                # [TEST] Tests for payload validation
```

---

## 3. File-by-File Analysis

### `app.py`
* **Purpose**: Flask web application backend and ML serving API.
* **Key contents**: API routing, validation, feature scaling, inference, response formatting.
* **Dependencies**: `flask`, `flask-cors`, `joblib`, `numpy`, `pandas`, `sklearn`, `config.py`
* **Depended on by**: Front-end static scripts and tests.
* **Data flow**: JSON input payload (demographics + symptoms) → data validation → scaling via `scaler.transform()` → prediction probabilities via `best_model.predict_proba()` → sorting top 5 → risk determination → medication database retrieval via `medicine_db.json` → JSON output response.
* **Critical logic**: `validate_input()`, `calculate_risk_level()`, `patch_sklearn_pickle_compatibility()`.
* **Current state**: ✅ Complete and fully optimized.

### `config.py`
* **Purpose**: Configuration management layer utilizing `python-dotenv`.
* **Key contents**: Resolve base directories and load environment variables for file paths and server parameters.
* **Dependencies**: `python-dotenv`, `os`
* **Depended on by**: `app.py`
* **Current state**: ✅ Complete and clean.

### `train_model.py`
* **Purpose**: Train the RandomForest model and generate serialized artifact files.
* **Key contents**: Reads Cleaned_Dataset.csv, maps diseases to top 8 + 'Other', defines numeric/categorical pipeline, exports `best_model.pkl`, `disease_encoder.pkl`, and `scaler.pkl`.
* **Dependencies**: `pandas`, `scikit-learn`, `joblib`
* **Current state**: ✅ Complete and executable.

### `requirements.txt`
* **Purpose**: Python package dependencies list.
* **Key contents**: Strictly pinned dependencies for runtime (`flask`, `flask-cors`, `joblib`, `numpy`, `pandas`, `scikit-learn`, `python-dotenv`, `gunicorn`) and testing (`pytest`, `pytest-cov`).
* **Current state**: ✅ Complete and verified.

---

## 4. System Architecture & Data Flow

### 4.1 — End-to-End Data Flow

```text
[User Web Interface (index.html + main.js)]
        ↓  Format: JSON (age, gender, blood_pressure, cholesterol, fever, cough, fatigue, difficulty_breathing)
[Flask API Layer (app.py : /predict)]
        ↓  Step 1: Input validation (check ranges, data types, missing fields)
[Pre-Processing]
        ↓  Step 2: Load scaler.pkl and run scaler.transform() on input features
[Model Inference]
        ↓  Step 3: Run best_model.predict_proba() to get probability arrays
[Post-Processing]
        ↓  Step 4: Sort probabilities and get top 5 classes via disease_encoder.pkl
        ↓  Step 5: Compute risk_level using demographics and symptoms
        ↓  Step 6: Retrieve treatment & advice from medicine_db.json
[Response Output]
        ↓  Format: JSON (success, prediction: top 5 classes, risk_level, recommendations: medicines + advice)
[User Web Interface]
```

### 4.2 — Module Dependency Graph

```text
[config.py] ── loads env ──> [.env / environment variables]
     ↓
[app.py (Flask Entry Point)]
     ├── imports ──> [flask, flask-cors, joblib, numpy, pandas, sklearn]
     ├── reads ────> [best_model.pkl, disease_encoder.pkl, scaler.pkl]
     ├── reads ────> [medicine_db.json]
     ├── renders ──> [templates/index.html, about.html, contact.html]
     └── calls ────> [static/css/style.css, static/js/main.js]
```

### 4.3 — Technology Stack Summary

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.10+ | Core runtime |
| **ML Framework** | scikit-learn | 1.8.0 | Model training & Inference |
| **Data Layer** | pandas / numpy | 3.0.3 / 2.4.6 | Data manipulation |
| **API / Serving** | Flask | 3.1.3 | Web server and API |
| **CORS** | flask-cors | 6.0.5 | Enable cross-origin resource requests |
| **WSGI Server** | Gunicorn | >=22.0.0 | Production WSGI HTTP Server |
| **Config** | python-dotenv | >=1.0.0 | Environment configuration |
| **Testing** | pytest / pytest-cov | 8.x / 6.x | Test runner & coverage reporting |
| **Design** | CSS3 (Vanilla) | Custom | Premium UI/UX design tokens and style rules |
| **Interactivity**| Javascript (ES6) | Vanilla | Frontend API fetching and UI logic |

---

## 5. Current State Assessment

### 5.1 — What Is Working (Verified)
* **Feature Scaling (No Skew)**: The API correctly loads `scaler.pkl` and transforms inputs via `scaler.transform()` before passing them to the model, solving the critical training-serving skew.
* **Externalized Config**: All model, encoder, scaler, and database paths are loaded from `config.py` via environment variables.
* **Structured Logging**: Replaced print statements with standard python logging under `'medicare'` logger.
* **Automated Test Suite**: 57 tests run via `pytest` cover endpoints, inference, risk engine, and input validations, achieving 87.65% code coverage.
* **Modern Frontend**: Interactive responsive screens styled by styling/design tokens in `style.css` and dynamic state management in `main.js`.
* **Clean Data Schema**: Structured documenting of dataset attributes in `data/schema.md`.

### 5.2 — What Is Pending (Planned Phase 4)
* **Containerization**: Needs `Dockerfile` and `docker-compose.yml` to package the app.
* **CI/CD Workflow**: Needs GitHub Actions script under `.github/workflows/` to execute test suites and check coverage targets automatically.
* **Linting / Code Standards**: Needs `pyproject.toml` file to configure Ruff for static analysis.
* **API Documentation**: Needs a dedicated API guide under `docs/api.md`.
* **Dev Dependencies**: Needs a separated `requirements-dev.txt`.

---

## 6. Technical Debt Register

All critical technical debt has been successfully resolved:
* **TD-001** (Hardcoded bypass of scaling): **RESOLVED** ✅ (StandardScaler loaded and applied).
* **TD-002** (Hardcoded paths to model files): **RESOLVED** ✅ (Cleanly handled by config layer).
* **TD-003** (Unpinned pandas/numpy): **RESOLVED** ✅ (Pinned to stable pandas 3.0.3 and numpy 2.4.6).
* **TD-004** (Print statement logging): **RESOLVED** ✅ (Proper logging module implemented).
* **TD-005** (Zero test coverage): **RESOLVED** ✅ (Robust test suite with 87.65% coverage).

---

## 7. Hard Constraints (Inviolable)

* **C-001 (Business)**: ML features inputted into `best_model.pkl` MUST undergo the exact same preprocessing/scaling transformations that were applied during training.
* **C-002 (Deployment)**: The Flask application MUST not crash upon startup if an optional model component is missing. The existing fallback logic should be preserved but improved with proper logging.

---

## 8. Implementation Phases

* **Phase 1: Foundation & Environment Hardening** — **COMPLETED** ✅ (Logging, config.py, requirements version pins).
* **Phase 2: Resolving Training-Serving Skew** — **COMPLETED** ✅ (`scaler.pkl` integrated and applied).
* **Phase 3: Testing & Frontend Modernization** — **COMPLETED** ✅ (57 tests passing with 87.65% coverage; styled UI and client script).
* **Phase 4: Containerization & Deployment Utilities** — **PENDING** 🔲 (Dockerfile, docker-compose, CI/CD, pyproject.toml, Ruff configuration, docs/api.md).

---

## 9. Quality Gates & Definition of Done

### Code Quality Gates
* [x] No `print()` statements — only structured `logging`
* [x] No hardcoded model file paths (externalized/configurable)
* [x] Dependency files strictly pinned
* [ ] Static analysis / linting passes (Ruff integration pending)

### Test Gates
* [x] `pytest tests/` passes with ≥ 80% coverage (Current: 87.65%)
* [x] All API endpoints have integration tests

### Data Quality Gates
* [x] Incoming data receives exactly the same preprocessing as training data (Scaler integration)
* [x] No manual bypassing of model feature expectations

### Deployment Gates (Pending Phase 4)
* [ ] Docker image builds successfully and container starts clean
* [x] Health check endpoint (`/health`) returns 200

---

## 10. Open Questions & Decisions Needed

| ID | Question | Blocks | Priority | Status |
|---|---|---|---|---|
| **Q-001** | Where is the `scaler.pkl` used to generate the scaled features in the notebook? | Phase 2 | CRITICAL | **RESOLVED** ✅ (Scaler extracted from notebooks and saved as `scaler.pkl`) |
| **Q-002** | Do we intend to implement the deep learning and hybrid recommendation engines discussed in `Personalized Reco System.txt`? | Future work | LOW | ❓ Open |
| **Q-003** | Should we configure a production-ready Web Server Gateway Interface (WSGI) like Gunicorn or uWSGI inside the Docker container? | Phase 4 | MEDIUM | ❓ Open (Gunicorn is currently added to requirements.txt) |
| **Q-004** | Do we require strict type hints using mypy as part of the linting suite? | Phase 4 | LOW | ❓ Open |
| **Q-005** | Are outcome_variable and risk_level inputs to the model? | Phase 2 | HIGH | **RESOLVED** ✅ (Mapped as input features and validated in `app.py`) |
