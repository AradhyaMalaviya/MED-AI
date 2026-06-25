# implementationplan2.md - Day 8 and Day 9 Detailed Action Plan

> Project: MediCare AI - Personalized Healthcare & Medicine Recommendation System  
> Scope: Day 8 containerization and Day 9 CI/CD, quality automation, and observability  
> App root: `Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare`  
> Deployment target: Platform-neutral Docker deployment  
> Monitoring depth: Full observability plan  
> Important rule: This file is an execution guide. It does not implement source-code changes by itself.

---

## 1. Current State Verified

### 1.1 Verified documentation context

The planning context comes from the `documentations/` folder:

| File | Role in this Day 8/9 plan |
|---|---|
| `AGENT_PROMPT.md` | Defines the audit-first, no-assumptions project planning method. |
| `AGENTS.md` | Confirms the real runnable app root and local command conventions. |
| `ARCHITECTURE_PLAN.md` | Defines runtime flow, logging expectations, failure modes, and non-negotiable rules. |
| `PRD.md` | Defines deployment, CI/CD, quality gates, and observability requirements. |
| `TECHSTACK.md` | Confirms Flask, scikit-learn, pytest, Gunicorn, Docker, and Ruff stack expectations. |
| `README.md` | Confirms local setup, app root, endpoints, environment variables, and troubleshooting notes. |
| `PROGRESS_AND_STATUS.md` | Confirms Days 1-7 are mostly completed and Days 8-10 are pending. |
| `plansdaybyday.md` | Defines Day 8 as Docker/Compose/Gunicorn and Day 9 as GitHub Actions/Ruff/monitoring. |
| `claude.md` | Confirms deployment utilities, CI/CD, Ruff, and API docs remain pending. |
| `implementation_plan.md` | Existing Day 8-only draft that this file extends and corrects. |

### 1.2 Verified application root

All implementation commands in this guide must run from:

```powershell
cd "C:\Users\deepa\Downloads\NEW PROJECT\Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)\medicare\medicare"
```

Do not run Docker, pytest, Ruff, or Gunicorn commands from the outer workspace root unless the command explicitly says so.

### 1.3 Verified source and artifact files in app root

| Path | Current role |
|---|---|
| `app.py` | Flask app, routes, validation, risk scoring, model loading, prediction response building. |
| `config.py` | Loads `.env`, centralizes model/database paths, host, port, and debug settings. |
| `train_model.py` | Offline retraining script that regenerates `best_model.pkl`, `disease_encoder.pkl`, and `scaler.pkl`. |
| `requirements.txt` | Runtime plus current test dependencies; already includes `gunicorn`. |
| `.env.example` | Existing environment template; needs Day 9 observability variables added later. |
| `.gitignore` | Existing ignore file; ignores `.pkl` model files and `.env`. |
| `.coveragerc` | Existing coverage config; needs Day 9 coverage gate correction. |
| `pytest.ini` | Existing pytest config; currently adds `--cov=.` by default. |
| `Cleaned_Dataset.csv` | Training dataset with 349 rows, 14 columns, 116 original disease labels, 49 duplicates, no nulls. |
| `medicine_db.json` | Active JSON medicine/advice database loaded by `app.py`. |
| `medicine_database.pkl` | Deprecated legacy pickle medicine database. |
| `best_model.pkl` | Required trained scikit-learn `Pipeline` artifact. |
| `disease_encoder.pkl` | Required label encoder; current model output space has 9 disease classes. |
| `scaler.pkl` | Required serving scaler for `age`, `blood_pressure`, and `cholesterol_level`. |
| `data/schema.md` | Dataset schema contract. |
| `templates/index.html` | Main diagnosis UI. |
| `templates/about.html` | About page UI. |
| `templates/contact.html` | Contact page UI. |
| `static/css/style.css` | Shared visual design system. |
| `static/js/main.js` | Frontend prediction fetch, result rendering, contact form, FAQ behavior. |
| `tests/conftest.py` | Flask client and mocked model/encoder/scaler fixtures. |
| `tests/test_endpoints.py` | Tests `/health`, `/models`, `/`, `/about`, and `/contact`. |
| `tests/test_predict.py` | Tests `/predict` success, top-five sorting, risk output, model/scaler failure paths. |
| `tests/test_risk_level.py` | Tests `calculate_risk_level()` branches and boundaries. |
| `tests/test_validation.py` | Tests validation success, missing fields, bad types, and range errors. |

### 1.4 Verified missing Day 8/9 files

The following files do not exist yet and must be created during Day 8/9 implementation:

| File | Intended day | Location |
|---|---:|---|
| `.dockerignore` | Day 8 | App root |
| `Dockerfile` | Day 8 | App root |
| `docker-compose.yml` | Day 8 | App root |
| `requirements-dev.txt` | Day 9 | App root |
| `pyproject.toml` | Day 9 | App root |
| `.github/workflows/ci.yml` | Day 9 | Repository root, not app root |

### 1.5 Verified test and coverage caveat

Current local baseline:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Expected current result:

```text
57 passed
app.py coverage around 87%
config.py coverage 100%
total coverage around 71% because train_model.py is included at 0%
```

This means a naive CI command like this will fail:

```powershell
python -m pytest --cov-fail-under=80
```

Reason:

- `pytest.ini` currently sets `--cov=.`.
- `.coveragerc` currently includes source files under the app root.
- `train_model.py` is an offline retraining script and is not exercised by the Flask API tests.
- Total coverage drops below 80 even though `app.py` itself passes the intended app coverage target.

Day 9 must fix this before enabling a coverage gate.

### 1.6 Verified Gunicorn caveat on Windows

Native Windows Gunicorn execution fails because Gunicorn is Unix/Linux-oriented:

```text
ModuleNotFoundError: No module named 'fcntl'
```

Therefore:

- Do not use native Windows Gunicorn as a required local acceptance check.
- Verify Gunicorn inside the Linux Docker container.
- For local Windows preflight before Docker, use Flask/test-client/pytest checks.

### 1.7 Verified CI artifact limitation

The `.pkl` files are intentionally ignored by Git:

- `best_model.pkl`
- `disease_encoder.pkl`
- `scaler.pkl`
- `medicine_database.pkl`

Impact:

- Local Docker builds can include these files because they exist on disk.
- GitHub Actions Docker builds may not have these files after checkout.
- CI can still run unit/integration tests because tests mock the model, encoder, and scaler.
- Full CI runtime smoke testing of a real model-loaded container requires a later artifact strategy.

Acceptable Day 9 default:

- Build the container image in CI.
- Do not require a model-loaded container smoke test in CI until model artifacts are supplied through Git LFS, release assets, cloud storage, encrypted CI artifacts, or a retraining step.

---

## 2. Day 8 - Containerization and Deployment Prep

### Day 8 goal

By the end of Day 8, the app must have a production-style Docker image, a Docker Compose configuration for local platform-neutral validation, and a verified Gunicorn runtime inside the Linux container.

### Day 8 success criteria

- `.dockerignore` exists in the app root.
- `Dockerfile` exists in the app root.
- `docker-compose.yml` exists in the app root.
- Docker image builds with `docker build -t medicare-ai .`.
- Container starts with Gunicorn.
- `/health` returns HTTP 200 from the running container.
- `/models`, `/`, `/about`, `/contact`, and `/predict` are manually smoke-tested.
- Docker Compose starts and stops the app cleanly.
- No `.env` or local caches are copied into the image.
- Required runtime artifacts are included in local Docker builds.

---

### Task 8.1 - Preflight the app root

#### Purpose

Confirm the current environment is ready before writing Docker files.

#### Commands

Run from the app root:

```powershell
cd "C:\Users\deepa\Downloads\NEW PROJECT\Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)\medicare\medicare"
```

Verify Docker:

```powershell
docker --version
docker compose version
```

Expected:

- Docker command exists.
- Docker Compose command exists.

Verify Python test baseline:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Expected:

- 57 tests pass.
- No test failures.
- Coverage output may show total coverage below 80 because of the current `train_model.py` coverage caveat; that gets fixed in Day 9.

Verify required runtime files exist:

```powershell
Test-Path app.py
Test-Path config.py
Test-Path requirements.txt
Test-Path medicine_db.json
Test-Path best_model.pkl
Test-Path disease_encoder.pkl
Test-Path scaler.pkl
Test-Path templates\index.html
Test-Path templates\about.html
Test-Path templates\contact.html
Test-Path static\css\style.css
Test-Path static\js\main.js
```

Expected:

- Every command returns `True`.

Confirm Day 8 files do not already exist:

```powershell
Test-Path Dockerfile
Test-Path .dockerignore
Test-Path docker-compose.yml
```

Expected before implementation:

- All return `False`.

#### Acceptance

- Preflight commands have been run.
- Any missing required runtime file is fixed before continuing.
- Docker file creation only begins after required runtime files exist.

---

### Task 8.2 - Create `.dockerignore`

#### File

`Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/.dockerignore`

#### Purpose

Keep the Docker build context clean and prevent local-only files, caches, coverage output, and secrets from entering the Docker image.

#### Exact file content

```text
# Virtual environments
venv/
.venv/
env/

# Python bytecode and caches
__pycache__/
**/__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# Test and coverage output
.coverage
htmlcov/
coverage.xml

# Local environment and secrets
.env
.env.*
!.env.example

# Version control
.git/
.gitignore

# Editor and OS files
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Build and packaging output
build/
dist/
*.egg-info/

# Logs
*.log
```

#### Important inclusion rule

Do not add these patterns to `.dockerignore`:

```text
*.pkl
medicine_db.json
templates/
static/
Cleaned_Dataset.csv
```

Reason:

- Local Docker builds need the model artifacts.
- The Flask UI needs templates and static assets.
- The active medicine database is `medicine_db.json`.
- `Cleaned_Dataset.csv` may be needed by training or diagnostic workflows; keep it available unless a later image-size decision removes it intentionally.

#### Verification

Run:

```powershell
Get-Content .dockerignore
```

Confirm:

- `venv/`, `.pytest_cache/`, `htmlcov/`, `.env`, `.git/`, editor files, and build output are excluded.
- `*.pkl` is not excluded.

#### Acceptance

- `.dockerignore` exists.
- Docker context excludes local/generated/secrets files.
- Required runtime assets are not accidentally excluded.

---

### Task 8.3 - Create `Dockerfile`

#### File

`Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/Dockerfile`

#### Purpose

Create a platform-neutral Linux image that installs dependencies, includes the Flask app, exposes port `5000`, checks `/health`, and runs under Gunicorn.

#### Exact file content

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000 \
    DEBUG=false

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
```

#### Why Python 3.11 slim

- It is Linux-based, so Gunicorn works.
- It is lighter than the full Python image.
- It avoids relying on the current Windows Python 3.14 local environment.
- It follows the existing Day 8 documentation.

#### Why install `curl`

- Docker healthcheck uses `curl`.
- `/health` is the official operational readiness endpoint.

#### Why copy `requirements.txt` before app files

- Docker can cache dependency installation.
- Source-only changes do not reinstall packages unless requirements change.

#### Why not run `python app.py`

- `python app.py` starts Flask's development server.
- Production/container runtime should use Gunicorn.

#### Gunicorn command explanation

| Flag | Purpose |
|---|---|
| `--bind 0.0.0.0:5000` | Listen on all interfaces inside the container. |
| `--workers 2` | Run two worker processes. |
| `--threads 2` | Allow each worker to process threaded requests. |
| `--timeout 60` | Avoid hanging requests forever. |
| `--access-logfile -` | Send access logs to stdout for Docker logs. |
| `--error-logfile -` | Send errors to stderr/stdout for Docker logs. |
| `app:app` | Load Flask object `app` from `app.py`. |

#### Verification

Run:

```powershell
docker build -t medicare-ai .
```

Expected:

- Image builds successfully.
- Dependencies install without conflict.
- Build output reaches the final image stage.

#### Acceptance

- `Dockerfile` exists.
- `docker build -t medicare-ai .` succeeds locally.
- No local virtual environment is copied into the image.

---

### Task 8.4 - Expand `/health` during implementation

#### File

`app.py`

#### Purpose

Make deployment checks confirm all required inference artifacts are available, not only the model and encoder.

#### Current behavior

`/health` currently returns:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "encoder_loaded": true,
  "message": "Backend is running!"
}
```

#### Target behavior

Keep existing keys and add new keys:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "encoder_loaded": true,
  "scaler_loaded": true,
  "medicine_db_loaded": true,
  "message": "Backend is running!"
}
```

#### Implementation steps

1. Locate `health_check()` in `app.py`.
2. Add `scaler_loaded: scaler is not None`.
3. Add `medicine_db_loaded: bool(medicine_db)`.
4. Keep existing keys unchanged for backward compatibility.
5. Do not expose file paths, exceptions, stack traces, or internal model details in `/health`.

#### Test update

Update `tests/test_endpoints.py`:

1. Keep the existing `status`, `model_loaded`, and `encoder_loaded` assertions.
2. Add assertions for:

```python
assert "scaler_loaded" in data
assert "medicine_db_loaded" in data
```

#### Acceptance

- `/health` remains HTTP 200.
- Existing tests still pass.
- New health fields appear in response JSON.
- Docker healthcheck still succeeds.

---

### Task 8.5 - Create `docker-compose.yml`

#### File

`Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/docker-compose.yml`

#### Purpose

Provide a single command to build, run, healthcheck, and stop the app locally in a Dockerized environment.

#### Exact file content

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: medicare-ai:latest
    container_name: medicare_ai_web
    ports:
      - "5000:5000"
    environment:
      HOST: "0.0.0.0"
      PORT: "5000"
      DEBUG: "false"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
    restart: unless-stopped
```

#### Why no bind mount by default

This compose file validates the actual container image.

Avoid this default:

```yaml
volumes:
  - .:/app
```

Reason:

- A bind mount can hide files baked into the image.
- It can accidentally make the container pass locally while the built image is broken.
- It can leak local-only files into runtime.

If a developer later wants hot reload, create a separate `docker-compose.dev.yml`.

#### Verification

Run:

```powershell
docker compose up -d --build
docker compose ps
curl.exe http://localhost:5000/health
docker compose logs --tail=100
docker compose down
```

Expected:

- Service starts.
- Health status becomes healthy.
- `/health` returns JSON.
- Logs show Gunicorn startup and request logs.
- Compose shutdown removes the running service.

#### Acceptance

- `docker-compose.yml` exists.
- `docker compose up -d --build` starts the app.
- `docker compose down` stops the app cleanly.

---

### Task 8.6 - Run the Docker image manually

#### Purpose

Verify the image outside Compose.

#### Build

```powershell
docker build -t medicare-ai .
```

Expected:

- Build succeeds.

#### Run

If a previous test container exists, remove it first:

```powershell
docker rm -f medicare_test_container
```

Start the container:

```powershell
docker run -d -p 5000:5000 --name medicare_test_container medicare-ai
```

Expected:

- Command returns a container ID.

Check status:

```powershell
docker ps
docker logs medicare_test_container --tail=100
```

Expected:

- Container is running.
- Logs show Gunicorn startup.

#### Verify `/health`

```powershell
curl.exe http://localhost:5000/health
```

Expected:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "encoder_loaded": true,
  "scaler_loaded": true,
  "medicine_db_loaded": true,
  "message": "Backend is running!"
}
```

#### Verify `/models`

```powershell
curl.exe http://localhost:5000/models
```

Expected:

- HTTP 200.
- JSON includes `available_models`, `current_model`, and `diseases_count`.
- `diseases_count` should be greater than `0`.

#### Verify HTML routes

```powershell
curl.exe -I http://localhost:5000/
curl.exe -I http://localhost:5000/about
curl.exe -I http://localhost:5000/contact
```

Expected:

- Each route returns HTTP 200.

#### Verify `/predict`

PowerShell command:

```powershell
$payload = @{
  age = 45
  gender = 1
  fever = 1
  cough = 1
  fatigue = 0
  breathing = 0
  bloodPressure = 1
  cholesterol = 1
  model = "rf"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:5000/predict" `
  -ContentType "application/json" `
  -Body $payload
```

Expected:

- `success` is `true`.
- Response includes `disease`, `confidence`, `risk`, `top5`, `medicines`, `advice`, `model_used`, and `timestamp`.

#### Inspect logs after requests

```powershell
docker logs medicare_test_container --tail=200
```

Expected:

- Startup logs show model, encoder, scaler, and medicine DB loading.
- Gunicorn access logs show route requests.

#### Cleanup

```powershell
docker stop medicare_test_container
docker rm medicare_test_container
```

#### Acceptance

- Manual image run works.
- Every smoke route works.
- Container cleanup completed.

---

### Task 8.7 - Document Day 8 known limitations

#### Add to implementation notes

Record these facts after Day 8:

1. Gunicorn is not validated natively on Windows because it requires Unix modules such as `fcntl`.
2. Gunicorn is validated inside Docker because the container uses Linux.
3. Local image builds include `.pkl` files only because they exist locally and are not excluded by `.dockerignore`.
4. GitHub Actions image builds need a later model artifact strategy before requiring a real model-loaded container smoke test.

#### Acceptance

- The project handoff notes do not imply Windows-native Gunicorn works.
- CI limitations are explicit.

---

## 3. Day 9 - CI/CD, Quality Automation, and Full Observability

### Day 9 goal

By the end of Day 9, every push and pull request should run automated linting, tests, coverage checks, and Docker image builds. The app should also have clear observability behavior: request logs, metrics, error counters, and optional third-party error tracking wiring.

### Day 9 success criteria

- Root-level `.github/workflows/ci.yml` exists.
- App-root `requirements-dev.txt` exists.
- App-root `pyproject.toml` exists.
- Coverage gate reaches at least 80% reliably.
- `python -m ruff check .` passes.
- `python -m pytest --cov-fail-under=80` passes after the coverage fix.
- Docker build job runs in CI.
- App has request timing logs without logging request bodies or personal health information.
- `/metrics` endpoint exists and can be disabled if needed.
- Error counters are tracked.
- Optional Sentry integration is controlled by environment variables and disabled by default.

---

### Task 9.1 - Decide CI file location correctly

#### File

Repository root:

```text
.github/workflows/ci.yml
```

Full local path:

```text
C:\Users\deepa\Downloads\NEW PROJECT\.github\workflows\ci.yml
```

#### Important rule

Do not create this workflow inside:

```text
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/.github/
```

Reason:

- GitHub Actions only reads workflows from repository-root `.github/workflows/`.

#### Acceptance

- `.github/workflows/ci.yml` exists at the repository root.
- The workflow sets the nested app root as its working directory.

---

### Task 9.2 - Create `requirements-dev.txt`

#### File

`Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/requirements-dev.txt`

#### Purpose

Separate development tools from runtime dependencies.

#### Exact file content

Use a pinned Ruff version at implementation time. Example:

```text
-r requirements.txt

ruff==0.14.9
```

#### Implementation steps

1. Check latest acceptable local Ruff version or choose a stable pinned version.
2. Add `-r requirements.txt` as the first line.
3. Add the pinned Ruff dependency.
4. If optional Sentry integration is implemented in source code during Day 9, add `sentry-sdk` to runtime or dev dependencies depending on whether production will import it unconditionally.

Recommended Sentry dependency rule:

- If `app.py` imports `sentry_sdk` only inside a guarded block and handles `ImportError`, place it in `requirements-dev.txt` only while optional.
- If production should support Sentry immediately when `SENTRY_DSN` is set, add a pinned `sentry-sdk` to `requirements.txt`.

#### Verification

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m ruff --version
```

Expected:

- Ruff is installed.
- Version is the pinned version.

#### Acceptance

- `requirements-dev.txt` exists.
- Dev dependencies install cleanly.

---

### Task 9.3 - Create `pyproject.toml` for Ruff

#### File

`Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/pyproject.toml`

#### Purpose

Configure Ruff linting consistently for local development and CI.

#### Exact file content

```toml
[tool.ruff]
target-version = "py311"
line-length = 120
extend-exclude = [
    "venv",
    ".venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "htmlcov",
    "build",
    "dist",
]

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
```

#### Implementation steps

1. Create `pyproject.toml` in the app root.
2. Run Ruff:

```powershell
.\venv\Scripts\python.exe -m ruff check .
```

3. Fix real lint errors in source files.
4. Do not edit generated files in `venv/`, `htmlcov/`, `.pytest_cache/`, or `__pycache__/`.

#### Acceptance

- Ruff config exists.
- `python -m ruff check .` passes.
- No generated/local-only files are linted.

---

### Task 9.4 - Fix the coverage gate

#### Files

Primary:

```text
.coveragerc
```

Optional:

```text
pytest.ini
```

#### Problem

Current `pytest.ini` uses:

```ini
--cov=.
```

That includes `train_model.py`, which is offline retraining code and has 0% coverage in the API test suite.

#### Preferred fix

Update `.coveragerc` so `train_model.py` is omitted from normal app coverage:

```ini
[run]
source = .
omit =
    tests/*
    __pycache__/*
    venv/*
    .venv/*
    train_model.py
```

#### Why this is preferred

- Normal `python -m pytest --cov-fail-under=80` becomes reliable.
- CI does not need a special coverage override.
- It aligns the coverage gate with the deployed Flask API.
- Offline retraining script coverage can be added later with dedicated tests.

#### Alternative if `.coveragerc` is not changed

Use this in CI:

```powershell
python -m pytest -o addopts="" --cov=app --cov=config --cov-report=term-missing --cov-fail-under=80
```

This is acceptable but less clean because it bypasses normal pytest defaults.

#### Verification

After the preferred `.coveragerc` fix:

```powershell
.\venv\Scripts\python.exe -m pytest --cov-fail-under=80
```

Expected:

- 57 tests pass.
- Coverage gate reaches at least 80%.

#### Acceptance

- Coverage gate passes locally.
- CI can run the same command.

---

### Task 9.5 - Create GitHub Actions CI workflow

#### File

`C:\Users\deepa\Downloads\NEW PROJECT\.github\workflows\ci.yml`

#### Purpose

Automate linting, tests, coverage gate, and Docker image builds on push and pull request.

#### Exact file content

```yaml
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

defaults:
  run:
    shell: bash
    working-directory: Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare

jobs:
  lint:
    name: Ruff lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
          cache-dependency-path: |
            Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/requirements.txt
            Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/requirements-dev.txt

      - name: Install dependencies
        run: python -m pip install -r requirements-dev.txt

      - name: Run Ruff
        run: python -m ruff check .

  test:
    name: Pytest and coverage
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
          cache-dependency-path: |
            Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/requirements.txt
            Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/requirements-dev.txt

      - name: Install dependencies
        run: python -m pip install -r requirements-dev.txt

      - name: Run tests
        run: python -m pytest --cov-fail-under=80

  docker-build:
    name: Docker build
    runs-on: ubuntu-latest
    needs:
      - lint
      - test
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t medicare-ai .
```

#### Important CI limitation

Because `.pkl` files are ignored by Git, the Docker build may fail in GitHub Actions if the Docker context requires files that are not present in the checkout.

If CI Docker build fails because model artifacts are missing, choose one of these follow-up approaches:

1. Use Git LFS for `.pkl` artifacts.
2. Download model artifacts from release assets during CI.
3. Download model artifacts from a private storage bucket using CI secrets.
4. Run `python train_model.py` during CI before `docker build`.
5. Split CI into:
   - normal tests/lint without artifacts,
   - image build only when artifacts are available.

Recommended Day 9 default:

- Keep Docker build job.
- If missing artifacts break CI, add an explicit artifact retrieval step rather than committing `.pkl` files directly.

#### Acceptance

- Workflow exists at repository root.
- Workflow uses nested app root as working directory.
- Lint job runs Ruff.
- Test job runs pytest with coverage gate.
- Docker build job runs after lint and test.

---

### Task 9.6 - Add observability configuration variables

#### File

`.env.example`

#### Purpose

Document operational toggles and optional third-party error tracking.

#### Add these variables

```env
# ---------- Observability ----------
# LOG_LEVEL=INFO
# ENABLE_METRICS=true
# SENTRY_DSN=
# SENTRY_ENVIRONMENT=local
```

#### File

`config.py`

#### Add these settings

```python
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "local")
```

#### Acceptance

- `.env.example` documents all new observability variables.
- `config.py` exposes typed/defaulted observability settings.
- App still starts without a `.env` file.

---

### Task 9.7 - Implement request timing logs

#### File

`app.py`

#### Purpose

Every request should log method, path, status, and duration without logging personal health input bodies.

#### Implementation steps

1. Add import:

```python
import time
from flask import g
```

If `g` is added to the existing Flask import line, the import becomes:

```python
from flask import Flask, request, jsonify, render_template, g
```

2. Use `LOG_LEVEL` from `config.py` when configuring logging:

```python
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
```

3. Add `before_request` handler:

```python
@app.before_request
def start_request_timer():
    g.request_start_time = time.perf_counter()
```

4. Add `after_request` handler:

```python
@app.after_request
def log_request(response):
    start_time = getattr(g, "request_start_time", None)
    duration_ms = 0.0
    if start_time is not None:
        duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s - %s - %.2fms",
        request.method,
        request.path,
        response.status_code,
        duration_ms,
    )
    return response
```

5. Remove or reduce any log line that prints full prediction request data:

Current risky line:

```python
logger.info("Received prediction request - data: %s", data)
```

Replace with non-PHI request summary:

```python
logger.info("Received prediction request")
```

or:

```python
logger.info("Received prediction request with validated fields: %s", sorted(data.keys()))
```

6. Keep detailed stack traces server-side with `logger.exception()` for unexpected failures.

#### Acceptance

- Logs include method, path, status, and duration for every route.
- Logs do not include request body values from `/predict`.
- Existing endpoint behavior stays the same.

---

### Task 9.8 - Add in-process metrics counters

#### File

`app.py`

#### Purpose

Expose lightweight Prometheus-style metrics for local and future production monitoring.

#### Metrics to track

| Metric | Type | Meaning |
|---|---|---|
| `medicare_requests_total` | counter | Total HTTP requests processed. |
| `medicare_errors_total` | counter | Total HTTP responses with status >= 500. |
| `medicare_prediction_requests_total` | counter | Total `/predict` requests processed. |
| `medicare_prediction_failures_total` | counter | Total failed prediction attempts. |
| `medicare_request_duration_ms_sum` | counter/sum | Sum of request durations in milliseconds. |
| `medicare_request_duration_ms_count` | counter | Count used to calculate average duration. |

#### Implementation approach

Use a simple in-memory dictionary for v1:

```python
metrics = {
    "requests_total": 0,
    "errors_total": 0,
    "prediction_requests_total": 0,
    "prediction_failures_total": 0,
    "request_duration_ms_sum": 0.0,
    "request_duration_ms_count": 0,
}
```

Update counters inside `after_request`:

```python
metrics["requests_total"] += 1
metrics["request_duration_ms_sum"] += duration_ms
metrics["request_duration_ms_count"] += 1
if response.status_code >= 500:
    metrics["errors_total"] += 1
```

Update prediction-specific counters in `/predict`:

```python
metrics["prediction_requests_total"] += 1
```

Increment prediction failures before returning prediction-related `500` responses and inside unexpected exception handling:

```python
metrics["prediction_failures_total"] += 1
```

#### Acceptance

- Metrics increment after requests.
- Metrics do not store personal health data.
- Metrics reset when the process restarts, which is acceptable for v1.

---

### Task 9.9 - Add `/metrics` endpoint

#### File

`app.py`

#### Purpose

Expose metrics in simple text format for Prometheus-style scraping or manual inspection.

#### Implementation steps

1. Import `Response`:

```python
from flask import Flask, request, jsonify, render_template, g, Response
```

2. Add route:

```python
@app.route("/metrics", methods=["GET"])
def metrics_endpoint():
    if not config.ENABLE_METRICS:
        return jsonify({
            "success": False,
            "error": "Metrics disabled",
        }), 404

    average_duration = 0.0
    if metrics["request_duration_ms_count"]:
        average_duration = (
            metrics["request_duration_ms_sum"] / metrics["request_duration_ms_count"]
        )

    body = "\n".join([
        "# HELP medicare_requests_total Total HTTP requests processed.",
        "# TYPE medicare_requests_total counter",
        f"medicare_requests_total {metrics['requests_total']}",
        "# HELP medicare_errors_total Total HTTP 5xx responses.",
        "# TYPE medicare_errors_total counter",
        f"medicare_errors_total {metrics['errors_total']}",
        "# HELP medicare_prediction_requests_total Total prediction requests.",
        "# TYPE medicare_prediction_requests_total counter",
        f"medicare_prediction_requests_total {metrics['prediction_requests_total']}",
        "# HELP medicare_prediction_failures_total Total failed prediction attempts.",
        "# TYPE medicare_prediction_failures_total counter",
        f"medicare_prediction_failures_total {metrics['prediction_failures_total']}",
        "# HELP medicare_request_duration_ms_avg Average request duration in milliseconds.",
        "# TYPE medicare_request_duration_ms_avg gauge",
        f"medicare_request_duration_ms_avg {average_duration:.2f}",
        "",
    ])
    return Response(body, mimetype="text/plain")
```

#### Verification

```powershell
curl.exe http://localhost:5000/metrics
```

Expected:

```text
medicare_requests_total ...
medicare_errors_total ...
medicare_prediction_requests_total ...
medicare_prediction_failures_total ...
medicare_request_duration_ms_avg ...
```

#### Test update

Add to `tests/test_endpoints.py`:

```python
def test_metrics_endpoint(app_client):
    response = app_client.get("/metrics")
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert b"medicare_requests_total" in response.data
```

#### Acceptance

- `/metrics` returns HTTP 200 when enabled.
- `/metrics` returns text/plain.
- Test passes.

---

### Task 9.10 - Add optional Sentry integration

#### Files

- `config.py`
- `app.py`
- `.env.example`
- `requirements.txt` or `requirements-dev.txt`

#### Purpose

Allow production error tracking without requiring Sentry locally.

#### Implementation approach

Add guarded initialization in `app.py`:

```python
if config.SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            environment=config.SENTRY_ENVIRONMENT,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.0,
        )
        logger.info("Sentry error tracking enabled")
    except ImportError:
        logger.warning("SENTRY_DSN is set but sentry-sdk is not installed")
```

#### Dependency decision

Recommended for production readiness:

```text
sentry-sdk[flask]==2.22.0
```

Pin the actual version during implementation.

Add to `requirements.txt` if production should support Sentry immediately.

Add to `requirements-dev.txt` only if Sentry remains documentation/demo-only.

#### Acceptance

- App starts when `SENTRY_DSN` is empty.
- App starts when `sentry-sdk` is absent and `SENTRY_DSN` is empty.
- If Sentry is configured, initialization is logged.
- No Sentry DSN is committed.

---

### Task 9.11 - Add observability tests

#### Files

- `tests/test_endpoints.py`
- `tests/test_predict.py`
- Optional new file: `tests/test_observability.py`

#### Required tests

1. `/health` includes new fields:

```python
def test_health_check_includes_artifact_flags(app_client):
    response = app_client.get("/health")
    data = response.get_json()
    assert "model_loaded" in data
    assert "encoder_loaded" in data
    assert "scaler_loaded" in data
    assert "medicine_db_loaded" in data
```

2. `/metrics` returns Prometheus-style text:

```python
def test_metrics_endpoint(app_client):
    response = app_client.get("/metrics")
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert b"medicare_requests_total" in response.data
```

3. Metrics increment after a route call:

```python
def test_metrics_increment_after_request(app_client):
    before = app_client.get("/metrics").data
    app_client.get("/health")
    after = app_client.get("/metrics").data
    assert after != before
```

4. Predict failure increments prediction failure counter:

Use existing `test_predict_model_not_loaded()` as the pattern and inspect `/metrics` after the failure.

5. Request logging does not include request body values:

Use `caplog` to assert route/status log exists while avoiding raw payload values.

Example:

```python
def test_request_logging_avoids_payload_values(app_client, valid_prediction_data, caplog):
    response = app_client.post("/predict", json=valid_prediction_data)
    assert response.status_code == 200
    logs = "\n".join(record.getMessage() for record in caplog.records)
    assert "POST /predict" in logs
    assert "45" not in logs
```

Adjust the exact value assertions carefully so unrelated timestamps/status values do not cause false positives.

#### Acceptance

- All existing tests pass.
- New observability tests pass.
- Coverage remains at or above 80%.

---

### Task 9.12 - Make error responses user-friendly

#### File

`app.py`

#### Purpose

Architecture docs require stack traces in logs, not in user responses.

#### Current risky behavior

Unexpected `/predict` exception response includes:

```python
"error": str(e)
```

This can leak internal details.

#### Target behavior

Keep full details in logs:

```python
logger.exception("Prediction failed")
```

Return generic response:

```python
return jsonify({
    "success": False,
    "error": "Prediction failed",
    "message": "Prediction failed. Please try again later."
}), 500
```

#### Test update

Add or update a test that forces an exception and confirms:

- Response status is 500.
- Response does not include file paths.
- Response does not include raw Python exception text.
- Server log records the exception.

#### Acceptance

- Stack traces remain server-side.
- Users receive generic, friendly error text.

---

### Task 9.13 - Add dashboard and alert wiring documentation

#### File options

Choose one during implementation:

1. Add a section to `documentations/README.md`.
2. Add a new `documentations/observability.md`.
3. Add a Day 9 subsection to the final handoff docs on Day 10.

Recommended Day 9 minimum:

- Add a concise section to `documentations/implementationplan2.md` completion notes or `documentations/README.md`.

#### Content to document

1. Metrics endpoint:

```text
GET /metrics
```

2. Example local check:

```powershell
curl.exe http://localhost:5000/metrics
```

3. Suggested alert thresholds:

| Signal | Suggested alert |
|---|---|
| Container healthcheck failing | Alert immediately after 3 consecutive failures. |
| HTTP 5xx rate | Alert if 5xx responses exceed 5% for 5 minutes. |
| Prediction failures | Alert if failures exceed 3 consecutive requests. |
| Average request duration | Alert if average exceeds 1000ms for 10 minutes. |
| Sentry errors | Alert on new unhandled exception type. |

4. Suggested dashboard panels:

| Panel | Source |
|---|---|
| Total requests | `medicare_requests_total` |
| 5xx errors | `medicare_errors_total` |
| Prediction requests | `medicare_prediction_requests_total` |
| Prediction failures | `medicare_prediction_failures_total` |
| Average latency | `medicare_request_duration_ms_avg` |
| Container health | Docker healthcheck and `/health` |

#### Acceptance

- Operators know how to inspect health, logs, and metrics.
- Alert thresholds are written down.

---

## 4. Final Day 8/9 Execution Order

Follow this order exactly:

1. Run Day 8 preflight from app root.
2. Create `.dockerignore`.
3. Create `Dockerfile`.
4. Add `/health` `scaler_loaded` and `medicine_db_loaded` fields.
5. Update health endpoint tests.
6. Build Docker image.
7. Run container manually.
8. Smoke-test `/health`, `/models`, `/`, `/about`, `/contact`, and `/predict`.
9. Stop and remove manual container.
10. Create `docker-compose.yml`.
11. Verify `docker compose up -d --build`.
12. Verify `docker compose down`.
13. Create `requirements-dev.txt`.
14. Create `pyproject.toml`.
15. Install dev dependencies.
16. Run Ruff and fix lint issues.
17. Fix coverage gate with `.coveragerc`.
18. Run `python -m pytest --cov-fail-under=80`.
19. Create repository-root `.github/workflows/ci.yml`.
20. Add observability config variables to `.env.example` and `config.py`.
21. Add request timing logs.
22. Remove raw request-body logging.
23. Add in-memory metrics counters.
24. Add `/metrics`.
25. Add optional Sentry initialization.
26. Add observability tests.
27. Add generic unexpected error response behavior.
28. Run full local validation.
29. Review Git diff.
30. Record unresolved artifact strategy for CI model-loaded container smoke tests.

---

## 5. Full Local Validation Checklist

Run from app root unless otherwise stated.

### 5.1 Python tests

```powershell
.\venv\Scripts\python.exe -m pytest
.\venv\Scripts\python.exe -m pytest --cov-fail-under=80
```

Expected:

- All tests pass.
- Coverage gate passes.

### 5.2 Ruff

```powershell
.\venv\Scripts\python.exe -m ruff check .
```

Expected:

- Zero Ruff errors.

### 5.3 Docker build

```powershell
docker build -t medicare-ai .
```

Expected:

- Image builds.

### 5.4 Docker run

```powershell
docker rm -f medicare_test_container
docker run -d -p 5000:5000 --name medicare_test_container medicare-ai
curl.exe http://localhost:5000/health
curl.exe http://localhost:5000/models
curl.exe http://localhost:5000/metrics
docker logs medicare_test_container --tail=100
docker stop medicare_test_container
docker rm medicare_test_container
```

Expected:

- Health returns 200.
- Model, encoder, scaler, and medicine DB flags are true locally.
- Metrics endpoint returns text.
- Logs show Gunicorn and route access.

### 5.5 Docker Compose

```powershell
docker compose up -d --build
docker compose ps
curl.exe http://localhost:5000/health
docker compose logs --tail=100
docker compose down
```

Expected:

- Compose service starts.
- Health check passes.
- Compose service stops cleanly.

### 5.6 GitHub Actions path check

Run from repository root:

```powershell
Test-Path .github\workflows\ci.yml
```

Expected:

- `True`

### 5.7 Git diff review

Run from repository root:

```powershell
git status --short
git diff -- .github\workflows\ci.yml
git diff -- "Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)\medicare\medicare"
```

Expected changed files after actual Day 8/9 implementation:

```text
.github/workflows/ci.yml
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/.dockerignore
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/Dockerfile
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/docker-compose.yml
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/requirements-dev.txt
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/pyproject.toml
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/.coveragerc
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/.env.example
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/config.py
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/app.py
Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare/tests/...
```

For this documentation-only task, expected changed file is only:

```text
documentations/implementationplan2.md
```

---

## 6. Public Interface Changes For Actual Day 8/9 Implementation

### `/health`

Backward-compatible expansion:

| Field | Required | Meaning |
|---|---|---|
| `status` | Existing | Service status string. |
| `model_loaded` | Existing | Whether `best_model.pkl` loaded. |
| `encoder_loaded` | Existing | Whether `disease_encoder.pkl` loaded. |
| `message` | Existing | Human-readable status. |
| `scaler_loaded` | New | Whether `scaler.pkl` loaded. |
| `medicine_db_loaded` | New | Whether `medicine_db.json` loaded and is non-empty. |

### `/metrics`

New endpoint:

```text
GET /metrics
```

Response:

- HTTP 200 when `ENABLE_METRICS=true`.
- HTTP 404 when `ENABLE_METRICS=false`.
- `text/plain` Prometheus-style metrics when enabled.

### Environment variables

New documented variables:

```env
LOG_LEVEL=INFO
ENABLE_METRICS=true
SENTRY_DSN=
SENTRY_ENVIRONMENT=local
```

---

## 7. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Native Windows Gunicorn fails with `fcntl` | Local production-server test fails on Windows | Validate Gunicorn inside Docker/Linux only. |
| `.pkl` files ignored by Git | GitHub CI cannot run real model-loaded container smoke tests by default | Add later artifact retrieval strategy. |
| Coverage gate fails because of `train_model.py` | CI blocks even though API code is covered | Omit `train_model.py` from API coverage or use app/config-only coverage command. |
| Request logging leaks health inputs | Privacy and compliance problem | Log route metadata only; never log full `/predict` payload values. |
| `/metrics` exposes operational info publicly | Low to medium operational exposure | Make metrics toggleable via `ENABLE_METRICS`; document production routing controls. |
| Sentry DSN committed accidentally | Secret leak | Keep `SENTRY_DSN` blank in `.env.example`; real value only in `.env` or platform secrets. |
| Docker image includes local caches | Bloated image and noisy builds | Use `.dockerignore` exactly as listed. |
| Compose bind mounts hide image problems | False positive local verification | Do not use bind mounts in default compose file. |

---

## 8. Definition of Done

Day 8 is done when:

- `.dockerignore`, `Dockerfile`, and `docker-compose.yml` exist in the app root.
- Docker build succeeds.
- Docker run succeeds.
- Gunicorn starts inside container.
- `/health`, `/models`, `/`, `/about`, `/contact`, and `/predict` smoke checks pass.
- Docker Compose start/stop works.

Day 9 is done when:

- Root `.github/workflows/ci.yml` exists and targets the nested app root.
- `requirements-dev.txt` exists and installs Ruff.
- `pyproject.toml` exists and configures Ruff.
- Ruff passes.
- Pytest passes.
- Coverage gate passes at 80% or higher.
- `/health` includes model, encoder, scaler, and medicine DB flags.
- `/metrics` exists and is tested.
- Request logs include method, path, status, and duration.
- Logs avoid request-body and personal health data.
- Optional Sentry wiring is documented and disabled by default.
- CI artifact limitation for `.pkl` files is documented.

---

## 9. Explicit Non-Goals For This Plan

This Day 8/9 plan does not require:

- Choosing AWS, Azure, GCP, Render, Railway, or any other host.
- Deploying to a live cloud environment.
- Committing `.pkl` artifacts to Git.
- Rewriting the Flask app into FastAPI.
- Replacing vanilla HTML/CSS/JS frontend.
- Retraining the model.
- Implementing deep learning or hybrid recommendation engines.
- Adding a database server.
- Adding patient data persistence.

---

## 10. Next Handoff Note

After this document is created, the next implementation session can safely start with:

1. Open `documentations/implementationplan2.md`.
2. Work through Day 8 tasks in order.
3. Run Day 8 validation.
4. Work through Day 9 tasks in order.
5. Run Day 9 validation.
6. Do not skip the `.pkl` CI artifact limitation.

