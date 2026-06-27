# Repository Guidelines

## Scope And Entry Points

This guide applies to the analyzed project directory:

`Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/`

The runnable Flask application is nested at:

`Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/`

Run application, test, and training commands from that inner `medicare/medicare/` folder unless a command says otherwise. The workspace root also contains research notebooks and project documents; keep those as reference material unless you are specifically updating planning or documentation.

## Complete Project Structure

The target project currently has one top-level folder:

| Path | Purpose |
|---|---|
| `medicare/` | Container folder for the application package. |
| `medicare/medicare/` | Actual app root containing Flask code, model artifacts, tests, assets, local environment output, and generated reports. |

Application-root folders:

| Folder | Contents and handling |
|---|---|
| `data/` | Data contract documentation. Currently contains `schema.md`. |
| `static/` | Frontend assets. Contains `css/style.css` and `js/main.js`. |
| `templates/` | Flask-rendered HTML pages: `index.html`, `about.html`, and `contact.html`. |
| `tests/` | Pytest suite plus shared fixtures. Source tests live beside a generated `__pycache__/`. |
| `htmlcov/` | Generated HTML coverage report from pytest-cov. Do not hand-edit. |
| `.pytest_cache/` | Generated pytest cache. Do not hand-edit. |
| `__pycache__/` | Generated Python bytecode cache for app modules. Do not hand-edit. |
| `venv/` | Local virtual environment with `Include/`, `Lib/`, `Scripts/`, `.gitignore`, and `pyvenv.cfg`. Recreate instead of editing. |

Application-root files:

| File | Purpose |
|---|---|
| `app.py` | Flask app, routes, validation, risk scoring, model loading, prediction response shaping, and fallback medicine data. |
| `config.py` | Centralizes `.env` loading, artifact paths, host, port, and debug settings. |
| `train_model.py` | Retrains the Random Forest pipeline and regenerates model artifacts from `Cleaned_Dataset.csv`. |
| `requirements.txt` | Runtime and dev/test Python dependencies. |
| `pytest.ini` | Test discovery, pytest markers, strict markers, and coverage defaults. |
| `.coveragerc` | Coverage source, omit rules, terminal report settings, and `htmlcov/` output directory. |
| `.env.example` | Template for optional local configuration. Copy to `.env`; never commit real secrets. |
| `.gitignore` | Ignores local envs, bytecode, secrets, model pickles, editor files, and build output. |
| `.coverage` | Generated coverage data file. Do not hand-edit. |
| `Cleaned_Dataset.csv` | Training dataset with 349 rows and columns documented in `data/schema.md`. |
| `best_model.pkl` | Serialized scikit-learn prediction pipeline loaded by `app.py`. |
| `disease_encoder.pkl` | Serialized label encoder used to map predictions to disease names. |
| `scaler.pkl` | Serialized scaler used for age, blood pressure, and cholesterol features. |
| `medicine_database.pkl` | Serialized legacy treatment recommendation database (deprecated). |
| `medicine_db.json` | Externalized disease-to-medicine/advice mapping database (JSON); loaded at startup by app.py; 13 disease entries. |

Generated coverage files in `htmlcov/` are `.gitignore`, `app_py.html`, `class_index.html`, `config_py.html`, `coverage_html_cb_188fc9a4.js`, `favicon_32_cb_c827f16f.png`, `function_index.html`, `index.html`, `keybd_closed_cb_900cfef5.png`, `status.json`, `style_cb_0853b3de.css`, and `train_model_py.html`.

Generated cache paths are `.pytest_cache/.gitignore`, `.pytest_cache/CACHEDIR.TAG`, `.pytest_cache/README.md`, `.pytest_cache/v/`, `.pytest_cache/v/cache/`, `.pytest_cache/v/cache/nodeids`, `__pycache__/app.cpython-314.pyc`, `__pycache__/config.cpython-314.pyc`, `tests/__pycache__/__init__.cpython-314.pyc`, `tests/__pycache__/conftest.cpython-314-pytest-9.1.0.pyc`, `tests/__pycache__/test_endpoints.cpython-314-pytest-9.1.0.pyc`, `tests/__pycache__/test_predict.cpython-314-pytest-9.1.0.pyc`, `tests/__pycache__/test_risk_level.cpython-314-pytest-9.1.0.pyc`, and `tests/__pycache__/test_validation.cpython-314-pytest-9.1.0.pyc`.

## Adjacent Workspace Files

Reference documents live in `documentations/`: `AGENTS.md`, `AGENT_PROMPT.md`, `ARCHITECTURE_PLAN.md`, `claude.md`, `plansdaybyday.md`, `PRD.md`, `PROGRESS_AND_STATUS.md`, and `README.md`. Root-level research artifacts are `Medicine_Recommendation_System.ipynb`, `Personalized_Medicine_Recommending_System (1).ipynb`, and `Personalized Reco System.txt`.

## Build, Test, And Development Commands

From the app root:

```powershell
cd "Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)\medicare\medicare"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
pytest
pytest --cov=. --cov-report=html
python train_model.py
```

`python app.py` starts Flask on `HOST` and `PORT` from `config.py` (`0.0.0.0:5000` by default). Use `/health` to confirm the backend and model/encoder loading, `/models` to inspect model metadata, and `/predict` for diagnosis requests. `pytest` runs tests with coverage because `pytest.ini` sets coverage addopts. `python train_model.py` retrains and rewrites `best_model.pkl`, `disease_encoder.pkl`, and `scaler.pkl`.

## Architecture And Runtime Flow

`app.py` loads model artifacts at import time using paths from `config.py`, applies compatibility patches for older scikit-learn pickles, serves `index.html`, `about.html`, and `contact.html`, and exposes JSON endpoints. `/predict` validates eight required fields, computes risk from symptoms, age, and blood pressure, converts frontend numeric inputs into training-data labels, scales numeric features, calls `best_model.predict()` and `predict_proba()`, returns top-five probabilities, and attaches medicine/advice recommendations.

The frontend in `templates/index.html` collects symptoms, patient details, and a visible model choice. `static/js/main.js` posts to `/predict`, renders confidence, risk, top-five diagnoses, treatment advice, and includes demo-mode fallback if the API call fails. Contact-page validation and FAQ behavior also live in `static/js/main.js`. `static/css/style.css` defines the shared visual system, layout, cards, forms, nav, toasts, responsive behavior, and animations for all pages.

## Data And Model Artifacts

Treat `data/schema.md` as the data contract before changing `Cleaned_Dataset.csv` or retraining. The dataset columns are `disease`, symptoms, `age`, `gender`, `blood_pressure`, `cholesterol_level`, `outcome_variable`, scaled numeric columns, and `risk_level`. Keep API preprocessing aligned with this schema. If a `.pkl` artifact changes, record how it was produced, rerun prediction tests, and note the changed artifact in review notes.

## Coding Style And Naming Conventions

Use Python 3, 4-space indentation, `snake_case` functions, and `UPPER_SNAKE_CASE` constants. Keep Flask route handlers readable and push reusable validation, scoring, model, or response logic into helpers. Match the current direct Flask style rather than adding a new framework layer. In templates, keep page names lowercase and route-aligned. In JavaScript, keep DOM IDs synchronized with `index.html` and `contact.html`; changing IDs requires updating `main.js` and tests or manual checks.

## Testing Guidelines

Tests use `pytest`, Flask's test client, `pytest-cov`, and fixtures from `tests/conftest.py`. The test suite contains 57 tests across 4 test files with 87.65% line coverage on `app.py`.

| Test file | Coverage area | Test Count / Details |
|---|---|---|
| `tests/__init__.py` | Marks `tests/` as a package. | — |
| `tests/conftest.py` | Provides mocked model, encoder, scaler, Flask client, and valid payload fixtures. | Setup fixtures |
| `tests/test_endpoints.py` | `/health`, `/models`, `/`, `/about`, and `/contact`. | 5 integration tests |
| `tests/test_predict.py` | Successful prediction shape, top-five sorting, risk output, and missing model/scaler failures. | 8 integration tests |
| `tests/test_risk_level.py` | High, medium, low, and boundary rules for `calculate_risk_level()`. | 22 unit tests |
| `tests/test_validation.py` | Valid payloads, missing fields, type errors, ranges, and mixed validation failures. | 21 unit tests |

Add or update tests whenever changing `validate_input()`, `calculate_risk_level()`, route behavior, response JSON, model preprocessing, templates served by routes, or frontend IDs expected by JavaScript.

## Generated And Local-Only Files

Do not manually edit generated files in `htmlcov/`, `.pytest_cache/`, `__pycache__/`, `tests/__pycache__/`, `.coverage`, or `venv/`. The current local `venv/` contains 12,238 files and 1,286 folders; recreate it from `requirements.txt` when it breaks. `htmlcov/` is recreated with `pytest --cov=. --cov-report=html`. Caches are recreated automatically by Python and pytest.

## Security And Configuration

Use `.env.example` as the only committed environment template. Put machine-specific values in `.env`, which is ignored. Supported variables are `MODEL_PATH`, `ENCODER_PATH`, `MEDICINE_DB_PATH`, `SCALER_PATH`, `PORT`, `HOST`, and `DEBUG`. Be careful with healthcare claims and personal data: the app should not persist patient inputs, and UI changes must preserve the medical disclaimer.

## Commit And Pull Request Guidelines

No Git repository was detected from the analyzed project path, so there is no local commit history to copy. Use concise imperative messages such as `Update prediction validation` or `Regenerate model artifacts`. Pull requests should include a summary, commands run, test results, affected files, screenshots for template/static changes, and explicit notes for changed `.pkl`, CSV, notebook, or generated report files.

## Agent-Specific Instructions

Before editing, confirm whether the change belongs in code (`medicare/medicare/`), documentation (`documentations/`), or research notebooks at the workspace root. Prefer source edits over generated output edits. Preserve the nested app-root assumption in all commands. After modifying runtime code, run `pytest`; after modifying UI, also start `python app.py` and manually check `/`, `/about`, `/contact`, and `/health` when practical.
