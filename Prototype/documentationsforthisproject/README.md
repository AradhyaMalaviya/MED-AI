# 🏥 MediCare AI — Local Setup Guide

> **Personalized Healthcare & Medicine Recommendation System**
>
> An ML-powered web application that predicts diseases from patient symptoms and vitals, then provides personalised medicine recommendations and health advice.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone / Locate the Project](#2-clone--locate-the-project)
3. [Create a Virtual Environment](#3-create-a-virtual-environment)
4. [Install Dependencies](#4-install-dependencies)
5. [Environment Configuration (Optional)](#5-environment-configuration-optional)
6. [Launch the Application](#6-launch-the-application)
7. [Using the Application](#7-using-the-application)
8. [API Reference](#8-api-reference)
9. [Running Tests](#9-running-tests)
10. [Project Structure](#10-project-structure)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites

| Requirement | Minimum Version | Check Command |
|---|---|---|
| **Python** | 3.10+ | `python --version` |
| **pip** | 22.0+ | `pip --version` |
| **Git** *(optional)* | Any | `git --version` |

> [!NOTE]
> The project has been tested on **Python 3.14.5** (Windows) but should work on any Python ≥ 3.10.

---

## 2. Clone / Locate the Project

If you already have the project folder, navigate to the **application root** — the directory that contains `app.py` and all the `.pkl` model files:

```bash
# The application root is nested inside the project:
cd "Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare"
```

The full path on the original machine is:

```
<project-root>/
  └── Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/
      └── medicare/
          └── medicare/          ← THIS is the application root
              ├── app.py
              ├── config.py
              ├── requirements.txt
              ├── best_model.pkl
              ├── scaler.pkl
              ├── disease_encoder.pkl
              ├── medicine_database.pkl
              └── templates/
```

> [!IMPORTANT]
> All commands below must be run from the **application root** (the directory containing `app.py`).

---

## 3. Create a Virtual Environment

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt after activation.

---

## 4. Install Dependencies

With the virtual environment **activated**, install all required packages:

```bash
pip install -r requirements.txt
```

### Core Dependencies

| Package | Purpose |
|---|---|
| `flask` | Web framework — serves the frontend and API |
| `flask-cors` | Cross-Origin Resource Sharing support |
| `scikit-learn` | ML model inference (Random Forest) |
| `pandas` | DataFrame construction for model input |
| `numpy` | Numerical operations |
| `joblib` | Model/scaler deserialization |
| `python-dotenv` | Environment variable management |

---

## 5. Environment Configuration (Optional)

The application works out of the box with sensible defaults. To customise settings, copy the example file:

```bash
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows
```

Then edit `.env` as needed:

```env
# ---------- Server Settings ----------
PORT=5000          # Port to run on (default: 5000)
HOST=0.0.0.0      # Bind address (default: 0.0.0.0)
DEBUG=false        # Enable Flask debug mode (default: false)

# ---------- Model Paths (defaults point to same directory) ----------
# MODEL_PATH=./best_model.pkl
# ENCODER_PATH=./disease_encoder.pkl
# MEDICINE_DB_PATH=./medicine_database.pkl
# SCALER_PATH=./scaler.pkl
```

> [!TIP]
> For development, set `DEBUG=true` to enable auto-reload on code changes.

---

## 6. Launch the Application

With the virtual environment activated:

```bash
python app.py
```

You should see output similar to:

```
2026-06-17 19:59:54 [INFO] medicare: Loading models...
2026-06-17 19:59:54 [INFO] medicare: Best model loaded from .../best_model.pkl
2026-06-17 19:59:54 [INFO] medicare: Label encoder loaded from .../disease_encoder.pkl
2026-06-17 19:59:54 [INFO] medicare: Scaler loaded from .../scaler.pkl
2026-06-17 19:59:54 [INFO] medicare: Medicine database loaded from .../medicine_database.pkl
2026-06-17 19:59:54 [INFO] medicare: Backend ready!
2026-06-17 19:59:54 [INFO] medicare: ============================================================
2026-06-17 19:59:54 [INFO] medicare: MEDICARE AI — BACKEND SERVER
2026-06-17 19:59:54 [INFO] medicare: ============================================================
 * Running on http://127.0.0.1:5000
```

### Open in Browser

Navigate to **http://127.0.0.1:5000** in your browser.

### Quick Health Check

Verify the backend is running and all models loaded:

```bash
curl http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "encoder_loaded": true,
  "message": "Backend is running!"
}
```

---

## 7. Using the Application

### Step-by-Step

1. **Open** `http://127.0.0.1:5000` in your browser
2. **Scroll down** to the "Smart Diagnosis System" section
3. **Select symptoms** by clicking the cards:
   - 🤒 Fever
   - 😷 Cough
   - 😴 Fatigue
   - 🫁 Difficulty Breathing
4. **Fill in patient details:**
   - Age (1–120)
   - Gender (Male / Female)
   - Blood Pressure (Low / Normal / High)
   - Cholesterol Level (Low / Normal / High)
5. **Choose an AI model** (Random Forest is recommended)
6. **Click** "🔬 Analyze & Diagnose"
7. **Review results:**
   - Predicted disease with confidence score
   - Risk level (Low 🟢 / Medium 🟡 / High 🔴)
   - Top 5 differential diagnoses
   - Recommended medicines with dosages
   - Medical advice and lifestyle recommendations

### Other Pages

| Page | URL | Description |
|---|---|---|
| Home | `/` | Main diagnosis interface |
| About | `/about` | Information about the system |
| Contact | `/contact` | Contact information |

---

## 8. API Reference

### `POST /predict`

The core prediction endpoint. Accepts patient data and returns disease predictions.

**Request:**

```json
{
  "age": 45,
  "gender": 1,
  "fever": 1,
  "cough": 1,
  "fatigue": 0,
  "breathing": 0,
  "bloodPressure": 1,
  "cholesterol": 1,
  "model": "rf"
}
```

**Field Reference:**

| Field | Type | Values | Required |
|---|---|---|---|
| `age` | int | 0 – 120 | ✅ |
| `gender` | int | `0` = Female, `1` = Male | ✅ |
| `fever` | int | `0` = No, `1` = Yes | ✅ |
| `cough` | int | `0` = No, `1` = Yes | ✅ |
| `fatigue` | int | `0` = No, `1` = Yes | ✅ |
| `breathing` | int | `0` = No, `1` = Yes | ✅ |
| `bloodPressure` | int | `0` = Low, `1` = Normal, `2` = High | ✅ |
| `cholesterol` | int | `0` = Low, `1` = Normal, `2` = High | ✅ |
| `model` | string | `"rf"`, `"gb"`, `"lr"` | ❌ |

**Success Response (200):**

```json
{
  "success": true,
  "disease": "Hypertension",
  "confidence": 87.23,
  "risk": "medium",
  "top5": [
    { "disease": "Hypertension", "confidence": 87.23 },
    { "disease": "Diabetes", "confidence": 6.11 }
  ],
  "medicines": ["💊 Lisinopril 10mg - Once daily morning", "..."],
  "advice": ["🧂 DIET: Drastically limit salt", "..."],
  "model_used": "rf",
  "timestamp": "2026-06-17T20:00:00"
}
```

### `GET /health`

Returns server and model status.

### `GET /models`

Lists available models and the count of diseases the system can predict.

---

## 9. Running Tests

The project includes unit and integration tests with `pytest`:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_predict.py -v
```

Current coverage: **87.65%** on `app.py` (exceeds the 80% target).

---

## 10. Project Structure

```
medicare/medicare/               ← Application Root
│
├── app.py                       # Flask backend — API endpoints & ML pipeline
├── config.py                    # Centralized configuration (paths, env vars)
├── train_model.py               # Model retraining script
├── requirements.txt             # Pinned Python dependencies
│
├── best_model.pkl               # Serialized Random Forest classifier
├── scaler.pkl                   # Feature scaler (StandardScaler for age, BP, cholesterol)
├── disease_encoder.pkl          # LabelEncoder mapping indices → disease names
├── medicine_database.pkl        # Legacy database (deprecated)
├── medicine_db.json             # Disease → medicines/advice lookup database (JSON)
├── Cleaned_Dataset.csv          # Cleaned training dataset
│
├── static/                      # Static assets (design system & interactive JS)
│   ├── css/
│   │   └── style.css            #   Premium CSS stylesheet (design tokens)
│   └── js/
│       └── main.js              #   Client-side interactive script
│
├── templates/                   # Flask HTML templates (frontend)
│   ├── index.html               #   Main diagnosis page
│   ├── about.html               #   About page
│   └── contact.html             #   Contact page
│
├── tests/                       # Test suite
│   ├── __init__.py              #   Package marker
│   ├── conftest.py              #   Shared test fixtures and Flask client
│   ├── test_predict.py          #   Integration tests for /predict
│   ├── test_endpoints.py        #   Endpoint integration tests
│   ├── test_risk_level.py       #   Unit tests for risk calculation
│   └── test_validation.py       #   Unit tests for input validation
│
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── pytest.ini                   # Pytest configuration
├── .coveragerc                  # Coverage configuration
└── data/                        # Data artifacts / schema definitions
    └── schema.md                #   Dataset schema documentation
```

### ML Artifact Files

These `.pkl` files are **required** for the application to function. They are pre-trained and included in the project:

| File | Contents | Size |
|---|---|---|
| `best_model.pkl` | Random Forest classifier pipeline (with preprocessing) | ~2.2 MB |
| `scaler.pkl` | StandardScaler fitted on training data (age, BP, cholesterol) | ~1 KB |
| `disease_encoder.pkl` | LabelEncoder mapping numeric predictions to disease names | ~350 B |
| `medicine_database.pkl` | Legacy dictionary database (deprecated) | ~10 KB |
| `medicine_db.json` | Disease → medicines/advice lookup database (JSON) | ~7.5 KB |

> [!CAUTION]
> Do **not** delete or modify the `.pkl` files unless you are retraining the model. The scaler must match the one used during training — otherwise all predictions will be incorrect.

---

## 11. Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'flask'`

**Cause:** Virtual environment is not activated, or dependencies were installed to the wrong Python.

**Fix:**
```bash
# Ensure venv is activated (you should see (venv) in your prompt)
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Then reinstall:
pip install -r requirements.txt
```

### ❌ `Failed to load best_model.pkl`

**Cause:** The `.pkl` model files are missing from the application root directory.

**Fix:** Ensure all four `.pkl` files (`best_model.pkl`, `scaler.pkl`, `disease_encoder.pkl`, `medicine_database.pkl`) are present in the same directory as `app.py`.

### ⚠️ `InconsistentVersionWarning: Trying to unpickle estimator from version X.X.X`

**Cause:** The model was trained with a different scikit-learn version than the one installed.

**Fix:** This is a **warning**, not an error. The application includes compatibility patches (`patch_sklearn_pickle_compatibility`) that handle this automatically. Predictions will still work correctly. To suppress warnings entirely, retrain the model with your current scikit-learn version:

```bash
python train_model.py
```

### ❌ `Address already in use` (Port 5000 conflict)

**Cause:** Another process is using port 5000.

**Fix:** Either stop the other process, or change the port:

```bash
# Option 1: Set via environment variable
set PORT=8080       # Windows CMD
$env:PORT=8080      # Windows PowerShell
export PORT=8080    # macOS/Linux

python app.py

# Option 2: Add to .env file
# PORT=8080
```

### ❌ Frontend shows "Connection Error" when clicking Predict

**Cause:** The frontend cannot reach the Flask server. This usually happens if the backend server isn't running or is listening on a different host/network interface.

**Fix:** Verify that the Flask server is running and that your browser has access to the port (default: 5000). The frontend utilizes relative URL paths (`/predict`) in `static/js/main.js`, meaning it adapts dynamically if hostnames or ports are configured via env variables.

### ❌ `execution of scripts is disabled on this system` (PowerShell)

**Cause:** PowerShell execution policy blocks the venv activation script.

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Quick Start (TL;DR)

```bash
# 1. Navigate to the app directory
cd "Personalized Healthcare & Medicine Recommendation System (Data ScienceML based)/medicare/medicare"

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows PowerShell
# source venv/bin/activate           # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the server
python app.py

# 5. Open in browser
# → http://127.0.0.1:5000
```

---

<p align="center">
  <strong>⚕️ MediCare AI</strong> — <em>AI-Powered Healthcare Diagnosis</em><br>
  <sub>⚠️ For informational purposes only. Always consult a qualified healthcare professional.</sub>
</p>
