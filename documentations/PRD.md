# 📋 Product Requirements Document (PRD)
# MediCare AI — Personalized Healthcare & Medicine Recommendation System

> **Version:** 1.0  
> **Date:** 2026-06-24  
> **Author:** Antigravity Pair Programming Session  
> **Status:** Updated & Approved  
> **Source Documents:** `AGENT_PROMPT.md` · `claude.md` · `plansdaybyday.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision & Objectives](#2-product-vision--objectives)
3. [Stakeholders & Target Users](#3-stakeholders--target-users)
4. [System Overview](#4-system-overview)
5. [Current State Assessment](#5-current-state-assessment)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [System Architecture](#8-system-architecture)
9. [Data Requirements](#9-data-requirements)
10. [API Specification](#10-api-specification)
11. [Technology Stack](#11-technology-stack)
12. [Frontend Requirements](#12-frontend-requirements)
13. [Machine Learning Pipeline Requirements](#13-machine-learning-pipeline-requirements)
14. [Security & Compliance Requirements](#14-security--compliance-requirements)
15. [Testing Strategy](#15-testing-strategy)
16. [Deployment & Infrastructure](#16-deployment--infrastructure)
17. [Implementation Roadmap](#17-implementation-roadmap)
18. [Risk Register](#18-risk-register)
19. [Technical Debt & Constraints](#19-technical-debt--constraints)
20. [Quality Gates & Acceptance Criteria](#20-quality-gates--acceptance-criteria)
21. [Open Questions & Decisions](#21-open-questions--decisions)
22. [Appendices](#22-appendices)

---

## 1. Executive Summary

### 1.1 — Product Overview

MediCare AI is a **Machine Learning-powered Personalized Medicine Recommendation System** delivered as an interactive web application. Users input demographic information (age, gender) and current symptoms (fever, cough, fatigue, difficulty breathing) along with clinical indicators (blood pressure level, cholesterol level). The system predicts potential diseases, calculates a patient-specific risk level, and provides tailored medicine recommendations, clinical advice, and lifestyle interventions.

### 1.2 — Problem Statement

Patients and frontline healthcare workers often lack rapid access to preliminary diagnostic guidance and medicine recommendations. Current approaches require specialist consultations that may not be immediately available, especially in underserved areas. There is a need for an intelligent triage tool that can provide **fast, evidence-informed preliminary assessments** to support — not replace — clinical decision-making.

### 1.3 — Proposed Solution

A production-grade web application backed by a scikit-learn classification model that:

- Accepts structured patient symptom and demographic data via a web form or API
- Predicts the most likely disease from a trained set of conditions
- Provides a confidence-ranked list of the top 5 most probable diseases
- Calculates a contextual risk level (Low / Medium / High)
- Returns tailored medicine recommendations and lifestyle advice for the predicted condition

### 1.4 — Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Prediction accuracy (known test cases) | ≥ 60% top-1 accuracy on validation set | Automated test suite |
| API response latency (P95) | ≤ 500ms | Request logging middleware |
| System uptime | ≥ 99% | Health check monitoring |
| Test coverage | ≥ 80% line coverage on `app.py` | `pytest-cov` |
| Training-serving feature alignment | 100% (zero skew) | Scaler integration validation |
| Medicine database coverage | 100% of model-predictable diseases | Audit against `label_encoder.classes_` |

---

## 2. Product Vision & Objectives

### 2.1 — Vision Statement

To build a reliable, accessible, and production-ready AI-powered preliminary diagnostic tool that empowers patients and healthcare workers with rapid, personalized health assessments and evidence-based medicine recommendations.

### 2.2 — Core Objectives

| ID | Objective | Priority |
|---|---|---|
| OBJ-01 | Deliver mathematically correct ML predictions with properly synchronized feature preprocessing | **CRITICAL** |
| OBJ-02 | Provide a polished, responsive, and intuitive web interface | HIGH |
| OBJ-03 | Ensure comprehensive medicine & advice coverage for all predictable diseases | HIGH |
| OBJ-04 | Achieve production-grade reliability via testing, logging, and containerization | HIGH |
| OBJ-05 | Enable reproducible, automated deployment via Docker and CI/CD | MEDIUM |
| OBJ-06 | Establish a maintainable, well-documented codebase for future extensibility | MEDIUM |

### 2.3 — Out of Scope (v1.0)

The following capabilities are referenced in the system design notes (`Personalized Reco System.txt`) but are explicitly **out of scope** for this release:

- Deep learning-based recommendation engines (CNN, RNN, transformers)
- NLP-based symptom parsing from free-text input
- Hybrid collaborative/content-based filtering
- JWT authentication and user account management
- Real-time patient health tracking
- Integration with external EHR/EMR systems
- Multi-language support

---

## 3. Stakeholders & Target Users

### 3.1 — Stakeholders

| Role | Responsibility |
|---|---|
| Project Owner / Developer | Builds, maintains, and deploys the application |
| ML Engineer | Trains, evaluates, and updates the classification model |
| End Users | Interact with the web interface for health assessments |

### 3.2 — Target Users

| User Persona | Description | Primary Use Case |
|---|---|---|
| **Patient** | An individual seeking a preliminary health assessment | Input symptoms → receive disease prediction + medicine recommendations |
| **Frontline Health Worker** | A nurse, pharmacist, or community health aide | Rapid triage tool for initial patient assessment |
| **Developer / ML Engineer** | Technical team maintaining the system | Model retraining, API maintenance, deployment |

---

## 4. System Overview

### 4.1 — High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                           │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ index    │  │ about    │  │ contact  │   HTML Templates      │
│  │ .html    │  │ .html    │  │ .html    │                       │
│  └────┬─────┘  └──────────┘  └──────────┘                      │
│       │ POST /predict (JSON)                                    │
└───────┼─────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────────────────┐
│                   Flask API Layer (app.py)                     │
│                                                               │
│  ┌───────────────┐  ┌────────────────┐  ┌───────────────┐     │
│  │ /predict      │  │ /health        │  │ /models       │     │
│  │ POST          │  │ GET            │  │ GET           │     │
│  └───────┬───────┘  └────────────────┘  └───────────────┘     │
│          ↓                                                    │
│  ┌───────────────────────────────────────────────────┐        │
│  │              Preprocessing Pipeline               │        │
│  │  Input Validation → Scaler Transform → DataFrame  │        │
│  └───────────────────────┬───────────────────────────┘        │
│                          ↓                                    │
│  ┌───────────────────────────────────────────────────┐        │
│  │           Model Inference Engine                  │        │
│  │  best_model.pkl → predict_proba() → top 5        │        │
│  └───────────────────────┬───────────────────────────┘        │
│                          ↓                                    │
│  ┌───────────────────────────────────────────────────┐        │
│  │           Post-Processing & Response              │        │
│  │  disease_encoder.pkl → Risk Level → Medicine DB   │        │
│  └───────────────────────────────────────────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

### 4.2 — End-to-End Data Flow

```
[User Web Interface (index.html)]
        ↓  Format: JSON {age, gender, symptoms, BP, cholesterol}
[Input Validation Layer]
        ↓  Validated & sanitized input
[Feature Preprocessing (scaler.pkl)]
        ↓  Scaled features: age_scaled, bp_scaled, chol_scaled
[Model Inference (best_model.pkl)]
        ↓  Predicted disease index + class probabilities
[Label Decoding (disease_encoder.pkl)]
        ↓  Human-readable disease name + top 5 predictions
[Risk Level Calculation]
        ↓  Risk: Low | Medium | High
[Medicine Lookup (medicine_db.json)]
        ↓  Medicines, dosages, advice, lifestyle interventions
[JSON Response → User Interface]
```

---

## 5. Current State Assessment

### 5.1 — What Is Working

| Component | Status | Notes |
|---|---|---|
| Flask API routing (`/health`, `/models`, `/predict`) | ✅ Functional | Routes initialize and respond correctly |
| Model loading (`best_model.pkl`) | ✅ Functional | Includes backward compatibility patch for `SimpleImputer` |
| Disease label decoding (`disease_encoder.pkl`) | ✅ Functional | — |
| Medicine database lookup (`medicine_db.json`) | ✅ Functional | Fully externalized to JSON file and loaded at startup |
| Feature Preprocessing (`scaler.pkl`) | ✅ Functional | Correctly loads scaler and applies `scaler.transform()` to inputs, resolving training-serving skew |
| Configuration Management (`config.py`) | ✅ Functional | Loaded via python-dotenv with environment variables |
| Logging & Observability | ✅ Functional | Standard python logging configured with `'medicare'` logger |
| Automated Test Suite | ✅ Functional | 57 unit and integration tests passing with 87.65% code coverage |
| HTML template rendering | ✅ Modernized | Polished, responsive UI with error handling, active nav, and loading states |

### 5.2 — What Is Broken (Critical Issues)

All critical issues are now **RESOLVED**:

| ID | Component | Status | Resolution |
|---|---|---|---|
| BUG-001 | Feature scaling (`app.py`) | **FIXED** ✅ | Integrated `scaler.pkl` and added `scaler.transform()` feature preprocessing. |
| BUG-002 | Configuration management | **FIXED** ✅ | Externalized configurations to `config.py` using `.env` variables. |
| BUG-003 | Error handling | **FIXED** ✅ | Implemented structured python logging to replace `print()` statements. |

### 5.3 — What Is Missing

| Component | Status | Impact |
|---|---|---|
| Feature scaler artifact (`scaler.pkl`) | ✅ **Completed** | Skew resolved |
| Automated test suite | ✅ **Completed** | 57 tests passing, 87.65% coverage |
| Input validation | ✅ **Completed** | Implemented `validate_input()` rules |
| Structured logging | ✅ **Completed** | Implemented structured `'medicare'` logging |
| `.gitignore` | ✅ **Completed** | Excluded configuration and model objects |
| `.env` / config management | ✅ **Completed** | Integrated `config.py` + `.env.example` |
| Dockerfile & docker-compose | 🔲 Missing | Needed for containerization (Phase 4) |
| CI/CD pipeline | 🔲 Missing | Needed for GitHub workflows (Phase 4) |
| API documentation | 🔲 Missing | Needed under `docs/api.md` (Phase 4) |

### 5.4 — Gap Summary

| Capability | Target State | Current State | Gap |
|---|---|---|---|
| ML Serving | Synchronized features via sklearn Pipeline & scaler | Preprocessed inputs via `scaler.transform()` | None ✅ |
| Configuration | Environment variables (`.env`) | Managed via `config.py` | None ✅ |
| Logging | Structured `logging` module | Structured logging with `'medicare'` logger | None ✅ |
| Testing | ≥80% coverage (unit & integration) | 57 tests with 87.65% line coverage | None ✅ |
| Deployment | Docker containerized | Local execution only | Needs `Dockerfile` and `docker-compose.yml` 🔲 |

---

## 6. Functional Requirements

### 6.1 — Disease Prediction (FR-001)

| Field | Detail |
|---|---|
| **ID** | FR-001 |
| **Priority** | CRITICAL |
| **Description** | The system shall accept patient demographic and symptom data and return a predicted disease with confidence scores. |
| **Input** | Age (int, 0–120), Gender (int, 0/1), Fever (int, 0/1), Cough (int, 0/1), Fatigue (int, 0/1), Difficulty Breathing (int, 0/1), Blood Pressure (int, 0–2), Cholesterol Level (int, 0–2) |
| **Output** | Predicted disease (string), confidence (float, 0–1), top 5 predictions with confidence scores |
| **Processing** | Input must be preprocessed using the exact same scaler transformations applied during model training |
| **Acceptance** | Predictions on known test cases match expected labels with ≥60% accuracy |

### 6.2 — Risk Level Assessment (FR-002)

| Field | Detail |
|---|---|
| **ID** | FR-002 |
| **Priority** | HIGH |
| **Description** | The system shall calculate a risk level based on symptom count, age, and clinical indicators. |
| **Logic** | `symptom_count ≥ 3 AND (age > 60 OR blood_pressure == 2)` → **High** · `symptom_count ≥ 2` → **Medium** · else → **Low** |
| **Output** | Risk level string: `"low"`, `"medium"`, or `"high"` |

### 6.3 — Medicine Recommendations (FR-003)

| Field | Detail |
|---|---|
| **ID** | FR-003 |
| **Priority** | HIGH |
| **Description** | For every predicted disease, the system shall return a list of recommended medicines with dosages, plus clinical and lifestyle advice. |
| **Data Source** | Externalized medicine database (`medicine_db.json`) |
| **Coverage** | Every disease in `label_encoder.classes_` must have a corresponding entry |
| **Fallback** | If no specific entry exists, return a generic "Consult your healthcare provider" response |

### 6.4 — Input Validation (FR-004)

| Field | Detail |
|---|---|
| **ID** | FR-004 |
| **Priority** | HIGH |
| **Description** | The system shall validate all incoming API requests and reject malformed input with descriptive error messages. |
| **Rules** | Age: int, 0–120 · Gender: int, 0/1 · Symptoms: int, 0/1 each · Blood Pressure: int, 0–2 · Cholesterol: int, 0–2 |
| **Error Handling** | Return `400 Bad Request` with a JSON body listing specific validation errors |

### 6.5 — Health Check (FR-005)

| Field | Detail |
|---|---|
| **ID** | FR-005 |
| **Priority** | MEDIUM |
| **Description** | The system shall expose a `/health` endpoint returning system status. |
| **Output** | `200 OK` with `{"status": "healthy"}` when all models are loaded |

### 6.6 — Model Information (FR-006)

| Field | Detail |
|---|---|
| **ID** | FR-006 |
| **Priority** | LOW |
| **Description** | The system shall expose a `/models` endpoint returning metadata about the loaded ML model. |

---

## 7. Non-Functional Requirements

### 7.1 — Performance

| Requirement | Target |
|---|---|
| API response time (P95) | ≤ 500ms |
| Concurrent request handling | Support ≥ 2 Gunicorn workers |
| Model loading time (startup) | ≤ 10 seconds |

### 7.2 — Reliability

| Requirement | Target |
|---|---|
| System uptime | ≥ 99% |
| Graceful degradation | App must not crash if `medicine_database.pkl` is missing (use fallback) |
| Health monitoring | `/health` endpoint with Docker `HEALTHCHECK` |

### 7.3 — Maintainability

| Requirement | Target |
|---|---|
| Test coverage | ≥ 80% line coverage |
| Linting | `ruff check .` passes with zero errors |
| Documentation | README enables new developer setup without external help |
| Configuration | All settings externalized to `.env` / environment variables |

### 7.4 — Observability

| Requirement | Target |
|---|---|
| Logging | Structured `logging` module with timestamps, severity levels, and module names |
| Request logging | Method, path, status code, and response time for every request |
| Error reporting | Stack traces in logs; user-friendly messages in API responses |

### 7.5 — Portability

| Requirement | Target |
|---|---|
| Containerization | Full Docker support with `Dockerfile` and `docker-compose.yml` |
| Environment independence | No hardcoded paths; all paths resolved relative to `__file__` or from env vars |

---

## 8. System Architecture

### 8.1 — Component Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  config.py   │  │   app.py     │  │  templates/  │     │
│  │  (Settings)  │  │  (Flask API) │  │  (Frontend)  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘     │
│         │                 │                                │
│  ┌──────┴─────────────────┴──────────────────────────┐    │
│  │              ML Inference Pipeline                 │    │
│  │                                                    │    │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────────┐   │    │
│  │  │ scaler.pkl │  │ model.pkl│  │ encoder.pkl  │   │    │
│  │  │ (Feature   │  │ (Classif │  │ (Label       │   │    │
│  │  │  Scaling)  │  │  ication)│  │  Decoding)   │   │    │
│  │  └────────────┘  └──────────┘  └──────────────┘   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Knowledge Base                            │    │
│  │  ┌──────────────────┐  ┌────────────────────┐      │    │
│  │  │ medicine_db.json │  │ Cleaned_Dataset.csv│      │    │
│  │  │ (Recommendations)│  │ (Training Data)    │      │    │
│  │  └──────────────────┘  └────────────────────┘      │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### 8.2 — Module Dependency Graph

```
[app.py (Flask Entry Point)]
    ├── imports → config.py (settings, paths)
    ├── imports → flask, scikit-learn, numpy, pandas, joblib
    ├── loads   → scaler.pkl (feature preprocessing)
    ├── loads   → best_model.pkl (ML classification model)
    ├── loads   → disease_encoder.pkl (label decoding)
    ├── loads   → medicine_db.json (medicine recommendations)
    └── renders → templates/ (index.html, about.html, contact.html)
```

---

## 9. Data Requirements

### 9.1 — Input Data Schema

| Field | Type | Range | Required | Description |
|---|---|---|---|---|
| `age` | integer | 0–120 | Yes | Patient age in years |
| `gender` | integer | 0, 1 | Yes | Patient gender (0 = Female, 1 = Male) |
| `fever` | integer | 0, 1 | Yes | Presence of fever symptom |
| `cough` | integer | 0, 1 | Yes | Presence of cough symptom |
| `fatigue` | integer | 0, 1 | Yes | Presence of fatigue symptom |
| `difficulty_breathing` | integer | 0, 1 | Yes | Presence of breathing difficulty |
| `blood_pressure` | integer | 0, 1, 2 | Yes | Blood pressure level (Low/Normal/High) |
| `cholesterol_level` | integer | 0, 1, 2 | Yes | Cholesterol level (Low/Normal/High) |

### 9.2 — Output Data Schema

| Field | Type | Description |
|---|---|---|
| `disease` | string | Predicted disease name |
| `confidence` | float (0–1) | Prediction confidence for top disease |
| `risk` | string | Risk level: `"low"`, `"medium"`, or `"high"` |
| `top5` | array of objects | Top 5 predictions, each with `disease` and `confidence`, sorted descending |
| `medicines` | array of objects | Recommended medicines with names and dosages |
| `advice` | array of strings | Clinical and lifestyle advice |

### 9.3 — Training Data

- **Source file:** `Cleaned_Dataset.csv`
- **Location:** `medicare/medicare/Cleaned_Dataset.csv`
- **Usage:** Used to train the scikit-learn classification model and fit the feature scaler
- **Requirement:** A formal data schema document (`data/schema.md`) must be created documenting all columns, types, and value ranges

### 9.4 — Model Artifacts

| Artifact | Format | Purpose | Status |
|---|---|---|---|
| `best_model.pkl` | Pickle (joblib) | Trained scikit-learn classifier | ✅ Exists |
| `disease_encoder.pkl` | Pickle (joblib) | `LabelEncoder` for disease target mapping | ✅ Exists |
| `medicine_database.pkl` | Pickle | Dictionary of medicine recommendations | ⚠️ Deprecated (replaced by medicine_db.json) |
| `medicine_db.json` | JSON | Disease-to-medicine/advice mapping database | ✅ Exists |
| `scaler.pkl` | Pickle (joblib) | `StandardScaler` / `MinMaxScaler` for feature scaling | ✅ Exists |

---

## 10. API Specification

### 10.1 — `POST /predict`

**Purpose:** Accept patient data and return disease prediction with recommendations.

**Request:**
```json
{
  "age": 45,
  "gender": 1,
  "fever": 1,
  "cough": 1,
  "fatigue": 0,
  "difficultyBreathing": 0,
  "bloodPressure": 1,
  "cholesterol": 1
}
```

**Response (200 OK):**
```json
{
  "disease": "Hypertension",
  "confidence": 0.87,
  "risk": "medium",
  "top5": [
    {"disease": "Hypertension", "confidence": 0.87},
    {"disease": "Diabetes", "confidence": 0.06},
    {"disease": "Heart Disease", "confidence": 0.03},
    {"disease": "Asthma", "confidence": 0.02},
    {"disease": "Stroke", "confidence": 0.02}
  ],
  "medicines": [
    {"name": "Amlodipine", "dosage": "5mg once daily"},
    {"name": "Lisinopril", "dosage": "10mg once daily"}
  ],
  "advice": [
    "Monitor blood pressure regularly",
    "Reduce sodium intake",
    "Exercise 30 minutes daily",
    "Manage stress through relaxation techniques"
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Validation failed",
  "details": [
    "age must be between 0 and 120",
    "fever must be 0 or 1"
  ]
}
```

### 10.2 — `GET /health`

**Purpose:** Health check endpoint for monitoring and container orchestration.

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

### 10.3 — `GET /models`

**Purpose:** Return metadata about the currently loaded ML model.

**Response (200 OK):**
```json
{
  "model_type": "scikit-learn classifier",
  "version": "1.8.0",
  "diseases_supported": 9
}
```

### 10.4 — `GET /`

**Purpose:** Serve the main web interface (`index.html`).

---

## 11. Technology Stack

| Layer | Technology | Version | Purpose | Status |
|---|---|---|---|---|
| Language | Python | 3.10+ | Core runtime | ✅ Present |
| ML Framework | scikit-learn | 1.8.0 | Model training & inference | ✅ Present |
| Data Layer | pandas / numpy | 3.0.3 / 2.4.6 | Data manipulation | ✅ Pinned & Present |
| API / Serving | Flask | 3.1.3 | Web framework & API | ✅ Present |
| CORS | flask-cors | 6.0.5 | Cross-origin requests | ✅ Present |
| Serialization | joblib | 1.5.3 | Model artifact loading | ✅ Present |
| WSGI Server | Gunicorn | >=22.0.0 | Production HTTP server | ✅ Present |
| Config | python-dotenv | >=1.0.0 | Environment variable management | ✅ Present |
| Testing | pytest / pytest-cov | 8.x / 6.x | Test framework & coverage | ✅ Present |
| Linting | ruff | Latest | Code quality enforcement | 🔲 To add (Phase 4) |
| Containerization | Docker | Latest | Deployment packaging | 🔲 To add (Phase 4) |
| CI/CD | GitHub Actions | — | Automated pipeline | 🔲 To add (Phase 4) |
| Orchestration | [NOT PRESENT] | — | Pipeline scheduling | ❌ Out of scope |
| Storage | Local filesystem (.csv, .json, .pkl) | — | Data & model persistence | ✅ Present |

---

## 12. Frontend Requirements

### 12.1 — Pages

| Page | File | Purpose |
|---|---|---|
| Main Dashboard | `index.html` | Patient data input form + prediction results display |
| About | `about.html` | Information about the system and its capabilities |
| Contact | `contact.html` | Contact information and feedback |

### 12.2 — UI/UX Requirements

| Requirement | Priority | Description | Status |
|---|---|---|---|
| Responsive design | HIGH | Must work on mobile, tablet, and desktop viewports | ✅ Completed |
| Loading states | HIGH | Visual spinner/indicator during API prediction calls | ✅ Completed |
| Error handling | HIGH | User-friendly error messages (not raw JSON) for failed predictions | ✅ Completed |
| Confidence visualization | MEDIUM | Visual meter/bar showing prediction confidence | ✅ Completed |
| Modern design system | MEDIUM | CSS variables, typography, color palette, consistent styling | ✅ Completed |
| Animations | LOW | Smooth transitions and micro-animations | ✅ Completed |
| Navigation consistency | MEDIUM | Uniform header, nav, and footer across all pages | ✅ Completed |
| Active page indication | LOW | Highlight the current page in navigation | ✅ Completed |

---

## 13. Machine Learning Pipeline Requirements

### 13.1 — Model Specifications

| Attribute | Detail |
|---|---|
| Model type | scikit-learn classifier (serialized via pickle/joblib) |
| Input features | Age, gender, symptoms (fever, cough, fatigue, breathing difficulty), blood pressure level, cholesterol level |
| Scaled features | `age_scaled`, `bp_scaled`, `chol_scaled` (via StandardScaler or MinMaxScaler) |
| Output | Disease class index + class probabilities |
| Artifacts | `best_model.pkl`, `disease_encoder.pkl`, `scaler.pkl` |

### 13.2 — Critical Constraint: Training-Serving Alignment (C-001)

> [!CAUTION]
> **INVIOLABLE CONSTRAINT:** ML features inputted into `best_model.pkl` MUST undergo the **exact same preprocessing/scaling transformations** that were applied during training in the notebook. Any deviation produces mathematically incorrect predictions.

**Current violation:** Lines 433–448 of `app.py` bypass scaling by assigning raw values directly:
```python
# BROKEN — currently in app.py
input_df["age_scaled"] = input_df["age"]       # ← WRONG: should be scaler.transform()
input_df["bp_scaled"] = input_df["blood_pressure"]
input_df["chol_scaled"] = input_df["cholesterol_level"]
```

**Required fix:**
```python
# CORRECT — target implementation
scaler = joblib.load(config.SCALER_PATH)
scaled_cols = ["age", "blood_pressure", "cholesterol_level"]
input_df[["age_scaled", "bp_scaled", "chol_scaled"]] = scaler.transform(input_df[scaled_cols])
```

### 13.3 — Scaler Export Requirement

The `StandardScaler` (or `MinMaxScaler`) used during training must be:
1. Located in the training notebooks (`Medicine_Recommendation_System.ipynb` or `Personalized_Medicine_Recommending_System (1).ipynb`)
2. Exported as `scaler.pkl` via `joblib.dump(scaler, 'scaler.pkl')`
3. Placed alongside the other `.pkl` artifacts in `medicare/medicare/`
4. Validated: `scaler.feature_names_in_` must match the columns it was trained on

---

## 14. Security & Compliance Requirements

### 14.1 — Secrets Management

| Requirement | Priority |
|---|---|
| No credentials or secrets in source code | CRITICAL |
| `.env` file excluded from Git via `.gitignore` | CRITICAL |
| `.env.example` with placeholder values provided | HIGH |
| Model artifacts (`.pkl`) excluded from Git | MEDIUM |

### 14.2 — Input Safety

| Requirement | Priority |
|---|---|
| All inputs validated for type, range, and presence | HIGH |
| Malformed requests return `400` (never crash) | HIGH |
| Error responses do not leak stack traces to users | HIGH |

### 14.3 — Medical Disclaimer

> [!IMPORTANT]
> The system provides **preliminary assessments only** and does not constitute medical advice. All outputs must include a disclaimer directing users to consult qualified healthcare professionals.

---

## 15. Testing Strategy

### 15.1 — Test Infrastructure

| Component | Tool | Configuration |
|---|---|---|
| Test runner | pytest | `pytest.ini` or `pyproject.toml` |
| Coverage | pytest-cov | `--cov-fail-under=80` |
| Fixtures | conftest.py | Flask test client, mock models, mock scaler |

### 15.2 — Unit Tests

| Test Suite | File | Coverage Target |
|---|---|---|
| Risk level calculation | `tests/test_risk_level.py` | All boundary conditions for low/medium/high |
| Input validation | `tests/test_validation.py` | ≥10 test cases (valid + invalid inputs) |

### 15.3 — Integration Tests

| Test Suite | File | Coverage Target |
|---|---|---|
| `/predict` endpoint | `tests/test_predict.py` | Valid request, response schema, top5 ordering, error scenarios |
| `/health` and `/models` endpoints | `tests/test_endpoints.py` | Status codes, response bodies |
| HTML template serving | `tests/test_endpoints.py` | `GET /` returns HTML |

### 15.4 — Validation Tests

| Test | Description |
|---|---|
| Known sample prediction | 3–5 rows from `Cleaned_Dataset.csv` sent to `/predict`; ≥3/5 must return correct disease |
| Scaler alignment | Verify `scaler.feature_names_in_` matches expected training columns |

---

## 16. Deployment & Infrastructure

### 16.1 — Docker

**Dockerfile requirements:**
- Base image: `python:3.11-slim`
- Working directory: `/app`
- Install dependencies via `requirements.txt`
- Expose port `5000`
- Healthcheck: `curl -f http://localhost:5000/health || exit 1` (30s interval, 5s timeout, 3 retries)
- Entrypoint: Gunicorn with 2 workers

**docker-compose.yml requirements:**
- Web service with volume mounts for development
- Port mapping: `5000:5000`
- Automatic `.env` loading

### 16.2 — CI/CD Pipeline (GitHub Actions)

**Workflow triggers:** Push to `main`, Pull Requests

**Jobs:**
1. **lint:** `ruff check .`
2. **test:** `pytest tests/ --cov=. --cov-fail-under=80`
3. **build:** `docker build .`

**Configuration:**
- Python 3.11 runner
- Pip dependency caching

### 16.3 — Production Server

| Setting | Value |
|---|---|
| WSGI Server | Gunicorn |
| Bind | `0.0.0.0:5000` |
| Workers | 2 |
| Environment | Configured via `.env` |

---

## 17. Implementation Roadmap

### 17.1 — Summary Calendar

```
┌────────────────────────────────────────────────────────────────┐
│  WEEK 1                                                        │
├──────┬─────────────────────────────────────────────────────────┤
│ DAY  │ FOCUS                                        │ EFFORT  │
├──────┼──────────────────────────────────────────────┼─────────┤
│  1   │ 🔧 Foundation: deps, config, logging, git    │  5–6 hr │
│  2   │ 🚨 CRITICAL: Fix training-serving skew       │  5–6 hr │
│  3   │ 🛡️ Input validation & data contracts         │  4–5 hr │
│  4   │ 🧪 Unit tests (risk calc, validation)        │  5–6 hr │
│  5   │ 🧪 Integration tests & coverage report       │  5 hr   │
├──────┴──────────────────────────────────────────────┴─────────┤
│  WEEK 2                                                        │
├──────┬──────────────────────────────────────────────┬─────────┤
│  6   │ 🎨 Frontend modernization & UX polish        │  6 hr   │
│  7   │ 💊 Medicine DB expansion & externalization   │  5–6 hr │
│  8   │ 🐳 Docker, docker-compose, Gunicorn          │  5 hr   │
│  9   │ ⚙️ CI/CD pipeline, linting, monitoring       │  5 hr   │
│ 10   │ 📝 Documentation, API docs, quality gates    │  5 hr   │
└──────┴──────────────────────────────────────────────┴─────────┘

Total: ~52 hours across 10 working days
```

### 17.2 — Critical Path

```
Day 1: Foundation
  └──> Day 2: Skew Fix 🚨
         └──> Day 3: Input Validation
                └──> Day 4: Unit Tests
                       └──> Day 5: Integration Tests
                              └──> Day 8: Docker
                                     └──> Day 9: CI/CD
                                            └──> Day 10: Docs & QA
```

**Parallel tracks:**
- Day 6 (Frontend) can run in parallel with Days 4–5
- Day 7 (Medicine DB) can run in parallel with Days 4–5
- Days 6 & 7 merge into Day 10 (Docs & QA)

### 17.3 — Phase Details

#### Phase 1: Foundation & Environment Hardening (Day 1)

| Task | File | Action | Priority |
|---|---|---|---|
| 1.1 Pin all dependencies | `requirements.txt` | MODIFY | HIGH |
| 1.2 Create config module | `config.py` (NEW) | CREATE | HIGH |
| 1.3 Replace print() with logging | `app.py` | MODIFY | HIGH |
| 1.4 Git hygiene & .gitignore | `.gitignore` (NEW) | CREATE | MEDIUM |

#### Phase 2: Training-Serving Skew Fix (Day 2) — CRITICAL

| Task | File | Action | Priority |
|---|---|---|---|
| 2.1 Extract & export scaler | Training notebooks | MODIFY | CRITICAL |
| 2.2 Integrate scaler into app | `app.py` | REFACTOR | CRITICAL |
| 2.3 Manual validation | — | VERIFY | CRITICAL |

#### Phase 3: Data Validation & Input Hardening (Day 3)

| Task | File | Action | Priority |
|---|---|---|---|
| 3.1 Request schema validation | `app.py` | MODIFY | HIGH |
| 3.2 Dataset schema documentation | `data/schema.md` (NEW) | CREATE | MEDIUM |

#### Phase 4: Unit Tests (Day 4)

| Task | File | Action | Priority |
|---|---|---|---|
| 4.1 Test infrastructure | `tests/`, `conftest.py`, `pytest.ini` (NEW) | CREATE | HIGH |
| 4.2 Risk level tests | `tests/test_risk_level.py` (NEW) | CREATE | HIGH |
| 4.3 Validation tests | `tests/test_validation.py` (NEW) | CREATE | HIGH |

#### Phase 5: Integration Tests (Day 5)

| Task | File | Action | Priority |
|---|---|---|---|
| 5.1 Predict endpoint tests | `tests/test_predict.py` (NEW) | CREATE | HIGH |
| 5.2 Auxiliary endpoint tests | `tests/test_endpoints.py` (NEW) | CREATE | MEDIUM |
| 5.3 Coverage report | — | VERIFY | HIGH |

#### Phase 6: Frontend Modernization (Day 6)

| Task | File | Action | Priority |
|---|---|---|---|
| 6.1 UI/UX redesign | `index.html`, `about.html`, `contact.html` | MODIFY | MEDIUM |
| 6.2 Navigation & consistency | All template files | MODIFY | MEDIUM |

#### Phase 7: Medicine Database Expansion (Day 7)

| Task | File | Action | Priority |
|---|---|---|---|
| 7.1 Audit coverage | — | VERIFY | HIGH |
| 7.2 Expand database | `COMPLETE_MEDICINE_DB` | MODIFY | HIGH |
| 7.3 Externalize to JSON | `medicine_db.json` (NEW) | CREATE | MEDIUM |

#### Phase 8: Containerization (Day 8)

| Task | File | Action | Priority |
|---|---|---|---|
| 8.1 Create Dockerfile | `Dockerfile` (NEW) | CREATE | HIGH |
| 8.2 Create docker-compose | `docker-compose.yml` (NEW) | CREATE | MEDIUM |
| 8.3 Gunicorn production server | — | VERIFY | HIGH |

#### Phase 9: CI/CD & Quality Automation (Day 9)

| Task | File | Action | Priority |
|---|---|---|---|
| 9.1 GitHub Actions workflow | `.github/workflows/ci.yml` (NEW) | CREATE | MEDIUM |
| 9.2 Linting with ruff | `pyproject.toml` (NEW) | CREATE | MEDIUM |
| 9.3 Error tracking & monitoring | `app.py` | MODIFY | MEDIUM |

#### Phase 10: Documentation & Handoff (Day 10)

| Task | File | Action | Priority |
|---|---|---|---|
| 10.1 Comprehensive README | `README.md` (NEW) | CREATE | HIGH |
| 10.2 API documentation | `docs/api.md` (NEW) | CREATE | MEDIUM |
| 10.3 Final quality gate checklist | — | VERIFY | HIGH |

---

## 18. Risk Register

### 18.1 — Known Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-001 | Training-serving feature skew | **Certain** (currently occurring) | CRITICAL | Export `scaler.pkl` from notebooks; integrate into `app.py` (Day 2) |
| R-002 | Unpinned dependency breakage | High | HIGH | Pin `pandas` and `numpy` to exact versions (Day 1) |
| R-003 | Directory restructuring breaks imports | Medium | MEDIUM | Use absolute path resolution via `os.path` relative to `__file__` |
| R-004 | Model performance degradation post-deployment | Medium | HIGH | Implement prediction logging; manual validation with known test cases |
| R-005 | Medicine database gaps for predicted diseases | Medium | MEDIUM | Audit `label_encoder.classes_` against `COMPLETE_MEDICINE_DB` keys (Day 7) |
| R-006 | Secrets committed to Git | Medium | HIGH | Create `.gitignore` excluding `.env` and `.pkl` files (Day 1) |

### 18.2 — Risk Matrix

```
         │  LOW Impact  │  MED Impact  │  HIGH Impact │  CRIT Impact │
─────────┼──────────────┼──────────────┼──────────────┼──────────────┤
HIGH     │              │              │    R-002     │    R-001     │
Likely   │              │              │              │              │
─────────┼──────────────┼──────────────┼──────────────┼──────────────┤
MEDIUM   │              │    R-005     │  R-003,R-006 │    R-004     │
Likely   │              │              │              │              │
─────────┼──────────────┼──────────────┼──────────────┼──────────────┤
LOW      │              │              │              │              │
Likely   │              │              │              │              │
─────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 19. Technical Debt & Constraints

### 19.1 — Technical Debt Register

| ID | Location | Description | Priority | Status |
|---|---|---|---|---|
| TD-001 | `app.py` | Hardcoded bypass of feature scaling | CRITICAL | **RESOLVED** ✅ |
| TD-002 | `app.py` | Hardcoded relative paths to `.pkl` model files | HIGH | **RESOLVED** ✅ |
| TD-003 | `requirements.txt` | `numpy` and `pandas` missing version constraints | HIGH | **RESOLVED** ✅ |
| TD-004 | `app.py` | Extensive use of `print()` for API logging | MEDIUM | **RESOLVED** ✅ |
| TD-005 | `app.py` | `COMPLETE_MEDICINE_DB` hardcoded inline | MEDIUM | **RESOLVED** ✅ |

### 19.2 — Hard Constraints (Inviolable)

| ID | Type | Constraint |
|---|---|---|
| C-001 | Business / ML | ML features inputted into `best_model.pkl` MUST undergo the exact same preprocessing/scaling transformations as during training |
| C-002 | Deployment | Flask app MUST NOT crash on startup if `medicine_database.pkl` is missing — fallback logic must be preserved |
| C-003 | Technical | Model artifacts are scikit-learn 1.6.1 compatible — runtime must match |

---

## 20. Quality Gates & Acceptance Criteria

### 20.1 — Code Quality Gates

- [ ] Zero `print()` statements — only structured `logging`
- [ ] No hardcoded model file paths (externalized via `config.py` + `.env`)
- [ ] All dependency versions strictly pinned in `requirements.txt`
- [ ] `ruff check .` passes with zero errors
- [ ] All functions have type annotations and docstrings

### 20.2 — Test Gates

- [ ] `pytest tests/` passes with ≥ 80% line coverage on `app.py`
- [ ] All API endpoints (`/predict`, `/health`, `/models`) have integration tests
- [ ] Risk level calculation has unit tests covering all boundary cases
- [ ] Input validation has ≥10 test cases covering valid and invalid inputs

### 20.3 — Data Quality Gates

- [ ] Incoming data receives the exact same preprocessing as training data (scaler integration)
- [ ] No manual bypassing of model feature expectations (lines 433–448 removed)
- [ ] Input validation rejects malformed requests with descriptive errors
- [ ] Every disease in `label_encoder.classes_` has a corresponding entry in the medicine database

### 20.4 — Deployment Gates

- [ ] Docker image builds successfully (`docker build -t medicare-ai .`)
- [ ] Container starts and `/health` returns `200`
- [ ] App runs under Gunicorn without errors
- [ ] `.env.example` documents all required environment variables
- [ ] No secrets committed to Git
- [ ] CI/CD pipeline passes on `main` branch

### 20.5 — Documentation Gates

- [ ] `README.md` enables new developer setup without external help
- [ ] `docs/api.md` documents every endpoint with examples
- [ ] `data/schema.md` documents the training dataset schema

---

## 21. Open Questions & Decisions

| ID | Question | Blocks | Priority | Status |
|---|---|---|---|---|
| Q-001 | Where is the scaler object in the training notebooks? Need to export `scaler.pkl`. | Day 2 (Critical Path) | 🔴 CRITICAL | **RESOLVED** ✅ (Extracted and loaded) |
| Q-002 | Should we implement the deep learning / hybrid recommendation engines from `Personalized Reco System.txt`? | Future roadmap | 🟡 LOW | ❓ Open |
| Q-003 | What cloud platform is the target for deployment (AWS, GCP, Azure, Railway, Render)? | Day 8 | 🟡 MEDIUM | ❓ Open |
| Q-004 | Is there a budget for monitoring/error tracking services (Sentry, Datadog)? | Day 9 | 🟢 LOW | ❓ Open |
| Q-005 | Do the `outcome_variable` and `risk_level` columns need to be in the input DataFrame, or are they artifacts of the training notebook? | Day 2 | 🔴 HIGH | **RESOLVED** ✅ (Required input features for best_model.pkl) |

---

## 22. Appendices

### Appendix A — File Inventory (Target State)

| File | Status | Phase |
|---|---|---|
| `app.py` | REFACTOR | 1, 2, 3 |
| `config.py` | CREATE | 1 |
| `requirements.txt` | MODIFY | 1 |
| `.env.example` | CREATE | 1 |
| `.gitignore` | CREATE | 1 |
| `scaler.pkl` | CREATE (from notebooks) | 2 |
| `data/schema.md` | CREATE | 3 |
| `tests/__init__.py` | CREATE | 4 |
| `tests/conftest.py` | CREATE | 4 |
| `tests/test_risk_level.py` | CREATE | 4 |
| `tests/test_validation.py` | CREATE | 4 |
| `tests/test_predict.py` | CREATE | 5 |
| `tests/test_endpoints.py` | CREATE | 5 |
| `templates/index.html` | MODIFY | 6 |
| `templates/about.html` | MODIFY | 6 |
| `templates/contact.html` | MODIFY | 6 |
| `medicine_db.json` | CREATE | 7 |
| `Dockerfile` | CREATE | 8 |
| `.dockerignore` | CREATE | 8 |
| `docker-compose.yml` | CREATE | 8 |
| `.github/workflows/ci.yml` | CREATE | 9 |
| `pyproject.toml` | CREATE | 9 |
| `requirements-dev.txt` | CREATE | 9 |
| `README.md` | CREATE | 10 |
| `docs/api.md` | CREATE | 10 |
| `pytest.ini` | CREATE | 4 |

### Appendix B — Reference Documents

| Document | Purpose | Path |
|---|---|---|
| Agent Prompt | Methodology blueprint for codebase analysis | `documentations/AGENT_PROMPT.md` |
| Implementation Plan | Current state assessment & architecture | `documentations/claude.md` |
| Day-by-Day Execution Plan | Sequenced task breakdown with acceptance criteria | `documentations/plansdaybyday.md` |
| System Design Notes | Vision for advanced features (future scope) | `Personalized Reco System.txt` |
| Flask Application | Core backend code | `medicare/medicare/app.py` |
| Training Dataset | Cleaned patient data | `medicare/medicare/Cleaned_Dataset.csv` |
| Training Notebook 1 | EDA and ML training | `Medicine_Recommendation_System.ipynb` |
| Training Notebook 2 | Alternative model training | `Personalized_Medicine_Recommending_System (1).ipynb` |

### Appendix C — Glossary

| Term | Definition |
|---|---|
| **Training-serving skew** | A mismatch between the data preprocessing applied during model training and at prediction (serving) time, causing incorrect results |
| **Feature scaling** | Normalizing numerical features (e.g., age, blood pressure) to a standard range, typically using `StandardScaler` or `MinMaxScaler` |
| **Label encoder** | A mapping from numerical class indices (model output) to human-readable disease names |
| **Quality gate** | A checkpoint that must pass before a phase or release is considered complete |
| **Technical debt** | Sub-optimal code or architecture choices that will cause problems at scale or in production |

---

> **Document Status:** Draft v1.0  
> **Next Action:** Resolve Q-001 (locate and export the scaler from training notebooks), then begin Day 1 implementation.
