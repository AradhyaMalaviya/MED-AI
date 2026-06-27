# 🏗️ Architecture Plan
# MediCare AI — Personalized Healthcare & Medicine Recommendation System

> **Version:** 1.0  
> **Date:** 2026-06-15  
> **Source Documents:** `AGENT_PROMPT.md` · `claude.md` · `plansdaybyday.md` · `PRD.md`

---

## Table of Contents

1. [What This Document Is](#1-what-this-document-is)
2. [What the System Does — In One Paragraph](#2-what-the-system-does--in-one-paragraph)
3. [The Main Components](#3-the-main-components)
4. [The Full User Journey — Step by Step](#4-the-full-user-journey--step-by-step)
5. [How the Components Interact — The Order of Operations](#5-how-the-components-interact--the-order-of-operations)
6. [How User Input Is Processed](#6-how-user-input-is-processed)
7. [How Tasks Are Tracked and Completed](#7-how-tasks-are-tracked-and-completed)
8. [How Success Is Confirmed](#8-how-success-is-confirmed)
9. [What Happens When Something Goes Wrong](#9-what-happens-when-something-goes-wrong)
10. [The Complete System Map](#10-the-complete-system-map)
11. [Key Rules the Architecture Must Follow](#11-key-rules-the-architecture-must-follow)
12. [Summary — The Architecture in 60 Seconds](#12-summary--the-architecture-in-60-seconds)

---

## 1. What This Document Is

This is the **architecture plan** for MediCare AI. It explains how every part of the system fits together, in plain language, following the real flow of the website from the moment a user opens it to the moment they close it.

It answers five questions:
1. What are the main parts of the system?
2. In what order do they talk to each other?
3. How is user input processed into a result?
4. How does the system know each step completed correctly?
5. How does the system confirm the final result is correct before showing it?

---

## 2. What the System Does — In One Paragraph

A person opens the MediCare AI website, fills in a form with their age, gender, symptoms (fever, cough, fatigue, breathing difficulty), blood pressure level, and cholesterol level. They press "Predict." The system takes that information, runs it through a trained machine learning model, figures out the most likely disease, calculates a risk level (low, medium, or high), looks up the right medicines and advice for that disease, and sends everything back to the screen — all within half a second. The user reads their result, and either tries again with different inputs or closes the page.

---

## 3. The Main Components

The system is made of **six parts**. Each one has a single clear job.

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ① FRONTEND              The web pages the user sees and uses      │
│   ② INPUT VALIDATOR        Checks that the user's data is correct   │
│   ③ FEATURE PREPROCESSOR   Transforms raw input into model-ready    │
│                            numbers (scaling)                        │
│   ④ PREDICTION ENGINE      The ML model that predicts the disease   │
│   ⑤ RESULT BUILDER         Assembles the final answer (disease,     │
│                            risk, medicines, advice)                 │
│   ⑥ CONFIGURATION LAYER    Manages settings, file paths, and        │
│                            environment variables                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

Here is what each component contains and does:

### ① Frontend (HTML Templates)

| Detail | Value |
|---|---|
| **Files** | `index.html`, `about.html`, `contact.html` |
| **Job** | Show the form, collect user input, display results |
| **Lives in** | `templates/` directory |

This is the only part the user sees. It has three pages:
- **Home (index.html):** The main page with the symptom form and the results area.
- **About (about.html):** Explains what the system is and how it works.
- **Contact (contact.html):** Provides contact information.

When the user fills in the form and clicks "Predict," the frontend sends the data to the backend as a JSON message and waits for a reply. When the reply comes back, it displays the disease, confidence score, risk level, medicines, and advice on screen.

---

### ② Input Validator

| Detail | Value |
|---|---|
| **Lives in** | `app.py` — `validate_input()` function |
| **Job** | Make sure the data the user sent is safe and makes sense |

Before the system does anything with the user's data, it checks every single field:

| Field | Valid Values | What happens if wrong |
|---|---|---|
| Age | A whole number, 0 to 120 | Rejected with error message |
| Gender | 0 (female) or 1 (male) | Rejected with error message |
| Fever | 0 (no) or 1 (yes) | Rejected with error message |
| Cough | 0 (no) or 1 (yes) | Rejected with error message |
| Fatigue | 0 (no) or 1 (yes) | Rejected with error message |
| Difficulty Breathing | 0 (no) or 1 (yes) | Rejected with error message |
| Blood Pressure | 0 (low), 1 (normal), or 2 (high) | Rejected with error message |
| Cholesterol | 0 (low), 1 (normal), or 2 (high) | Rejected with error message |

If anything is wrong, the system stops immediately and sends back a clear error message. It never passes bad data forward.

---

### ③ Feature Preprocessor

| Detail | Value |
|---|---|
| **Lives in** | `app.py` — uses `scaler.pkl` |
| **Job** | Transform raw numbers into the exact format the ML model expects |

This is the most **critical** component in the architecture. The ML model was trained on data where age, blood pressure, and cholesterol were mathematically scaled (normalized). If the system sends raw numbers (like `age = 45`) instead of scaled numbers (like `age_scaled = -0.23`), the model produces garbage predictions.

**How it works:**
1. Takes the validated user input (e.g., `age = 45`, `blood_pressure = 2`, `cholesterol = 1`)
2. Loads the same scaler object (`scaler.pkl`) that was used during model training
3. Transforms the three numeric columns into their scaled versions
4. Passes the correctly scaled data onward to the model

> ⚠️ **Architectural Rule:** The scaler used here MUST be the exact same scaler that was used during training. No exceptions. No shortcuts. If this rule is broken, every prediction will be wrong.

---

### ④ Prediction Engine

| Detail | Value |
|---|---|
| **Lives in** | `app.py` — uses `best_model.pkl` + `disease_encoder.pkl` |
| **Job** | Take the prepared data and predict which disease the user most likely has |

**How it works:**
1. Receives the preprocessed DataFrame (with correctly scaled features)
2. Runs `model.predict_proba()` to get the probability of every disease
3. Picks the disease with the highest probability as the primary prediction
4. Sorts all diseases by probability and takes the top 5
5. Uses `disease_encoder.pkl` to convert numeric indices back to disease names (e.g., `3` → `"Hypertension"`). Note that the training script `train_model.py` maps diseases to top 8 (Asthma, Bronchitis, Diabetes, Hypertension, Influenza, Migraine, Osteoporosis, Stroke) plus 'Other' for a total of 9 model classes.

**Output:** The predicted disease name, a confidence score (0 to 1), and a ranked list of the top 5 most likely diseases with their confidence scores.

---

### ⑤ Result Builder

| Detail | Value |
|---|---|
| **Lives in** | `app.py` — uses `medicine_db.json` |
| **Job** | Assemble the complete response: disease + risk level + medicines + advice |

**How it works:**

**Step A — Calculate Risk Level:**

The system looks at three things to determine how urgent the situation is:

```
Count the symptoms that are present (fever + cough + fatigue + breathing difficulty)

IF symptom_count ≥ 3 AND (age > 60 OR blood_pressure is HIGH):
    → Risk = HIGH

ELSE IF symptom_count ≥ 2:
    → Risk = MEDIUM

ELSE:
    → Risk = LOW
```

**Step B — Look Up Medicines & Advice:**

The system searches the medicine database (`medicine_db.json`) for the predicted disease and pulls out:
- Recommended medicines with dosages
- Clinical advice (what to do next)
- Lifestyle recommendations (diet, exercise, habits)

The `medicine_db.json` contains entries for: Influenza, Asthma, Diabetes, Hypertension, Pneumonia, Common Cold, Bronchitis, Depression, Stroke, Anxiety Disorders, Migraine, Osteoporosis, and Other.

If the disease isn't found in the database, it returns a safe fallback: *"Please consult a qualified healthcare professional."*

**Step C — Package the Response:**

Everything is assembled into a single JSON response:

```json
{
  "disease": "Hypertension",
  "confidence": 0.87,
  "risk": "medium",
  "top5": [
    {"disease": "Hypertension", "confidence": 0.87},
    {"disease": "Diabetes", "confidence": 0.06},
    ...
  ],
  "medicines": [
    {"name": "Amlodipine", "dosage": "5mg once daily"},
    ...
  ],
  "advice": [
    "Monitor blood pressure regularly",
    "Reduce sodium intake",
    ...
  ]
}
```

---

### ⑥ Configuration Layer

| Detail | Value |
|---|---|
| **Lives in** | `config.py` + `.env` file |
| **Job** | Store all settings in one place so nothing is hardcoded in the application code |

This component manages:
- File paths to all model artifacts (`best_model.pkl`, `disease_encoder.pkl`, `scaler.pkl`, `medicine_db.json`)
- Server settings (port number, debug mode)
- Any secrets or environment-specific values

The rule is simple: **`app.py` never contains any file path strings or configuration values.** Everything comes from `config.py`, which reads from environment variables or an `.env` file.

---

## 4. The Full User Journey — Step by Step

This section walks through everything that happens from the moment a user opens the website to when they close it. Every step is numbered. Nothing is skipped.

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  STEP 1:  User opens the website                                    │
│  STEP 2:  User sees the home page with the health form              │
│  STEP 3:  User fills in their information                           │
│  STEP 4:  User clicks "Predict"                                     │
│  STEP 5:  Frontend sends the data to the backend                    │
│  STEP 6:  Backend validates the input                               │
│  STEP 7:  Backend scales the numeric features                       │
│  STEP 8:  Backend runs the ML model                                 │
│  STEP 9:  Backend calculates risk level                             │
│  STEP 10: Backend looks up medicines and advice                     │
│  STEP 11: Backend sends the complete result back                    │
│  STEP 12: Frontend displays the result to the user                  │
│  STEP 13: User reads the result                                     │
│  STEP 14: User decides: try again, browse other pages, or leave     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

Here is each step in detail:

---

### STEP 1 — User Opens the Website

The user types the website address into their browser (e.g., `http://localhost:5000`). The browser sends a `GET /` request to the Flask server.

**What the server does:** Flask receives the request, finds the `index.html` template, and sends back the complete web page.

**What the user sees:** The MediCare AI home page loads with a health assessment form.

---

### STEP 2 — User Sees the Home Page

The page contains:
- A navigation bar (links to Home, About, Contact)
- A headline explaining what the tool does
- A medical disclaimer (this is not a replacement for a real doctor)
- The health assessment form
- An empty results area (hidden until a prediction is made)

---

### STEP 3 — User Fills In Their Information

The user fills in 8 fields:

| What they enter | Example |
|---|---|
| Age | 45 |
| Gender | Male |
| Fever? | Yes |
| Cough? | Yes |
| Fatigue? | No |
| Difficulty breathing? | No |
| Blood pressure level | Normal |
| Cholesterol level | Normal |

The form uses dropdowns and number inputs to prevent obviously wrong data (like typing "abc" in the age field).

---

### STEP 4 — User Clicks "Predict"

The user presses the submit button. The frontend:
1. Shows a **loading spinner** so the user knows something is happening
2. Disables the submit button to prevent double-clicking
3. Collects all form data into a structured JSON object
4. Sends it to the server

---

### STEP 5 — Frontend Sends Data to the Backend

The frontend makes a `POST /predict` request with this JSON body:

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

The request travels from the browser → to the Flask server → to the `/predict` route handler in `app.py`.

---

### STEP 6 — Backend Validates the Input

**Component responsible:** ② Input Validator

The server runs `validate_input(data)`, which checks every field:

```
✓ Is "age" present?          → Yes
✓ Is "age" a number?         → Yes (45)
✓ Is "age" between 0–120?    → Yes
✓ Is "gender" 0 or 1?        → Yes (1)
✓ Is "fever" 0 or 1?         → Yes (1)
✓ Is "cough" 0 or 1?         → Yes (1)
✓ Is "fatigue" 0 or 1?       → Yes (0)
✓ Is "difficultyBreathing" 0 or 1? → Yes (0)
✓ Is "bloodPressure" 0, 1, or 2?  → Yes (1)
✓ Is "cholesterol" 0, 1, or 2?    → Yes (1)

Result: ALL VALID → proceed to Step 7
```

**If any field fails:** The server immediately returns a `400 Bad Request` error with a list of what's wrong. The frontend hides the spinner and shows the error messages. The process stops here.

---

### STEP 7 — Backend Scales the Numeric Features

**Component responsible:** ③ Feature Preprocessor

The server takes the validated data and transforms it for the model:

```
Raw Input                         Scaled Output
─────────────────────────────     ──────────────────────
age = 45                    →     age_scaled = -0.23
blood_pressure = 1          →     bp_scaled = 0.01
cholesterol_level = 1       →     chol_scaled = 0.01
```

*(The actual scaled values depend on the scaler that was fit during training.)*

The system also builds a complete DataFrame with all the columns the model expects:
- The 4 symptom columns (fever, cough, fatigue, difficulty_breathing) — kept as-is (0 or 1)
- The gender column — kept as-is (0 or 1)
- The 3 scaled columns (age_scaled, bp_scaled, chol_scaled) — just computed
- Any other columns the model expects — set to their correct default values

---

### STEP 8 — Backend Runs the ML Model

**Component responsible:** ④ Prediction Engine

```
Input DataFrame (1 row, all features correctly scaled)
                    ↓
          best_model.pkl
      model.predict_proba()
                    ↓
    Probability for every disease:
    ┌──────────────────────────────┐
    │ Hypertension    → 0.87      │
    │ Diabetes        → 0.06      │
    │ Heart Disease   → 0.03      │
    │ Asthma          → 0.02      │
    │ Stroke          → 0.02      │
    │ Migraine        → 0.00      │
    │ ...             → ...       │
    └──────────────────────────────┘
                    ↓
          disease_encoder.pkl
    Decode index → disease name
                    ↓
    Primary Prediction: "Hypertension" (87% confidence)
    Top 5: [Hypertension, Diabetes, Heart Disease, Asthma, Stroke]
```

---

### STEP 9 — Backend Calculates Risk Level

**Component responsible:** ⑤ Result Builder (Part A)

```
Symptom count = fever(1) + cough(1) + fatigue(0) + breathing(0) = 2
Age = 45
Blood pressure = 1 (Normal)

Check HIGH:  symptom_count ≥ 3 AND (age > 60 OR bp == 2)?
             2 ≥ 3? NO → skip

Check MEDIUM: symptom_count ≥ 2?
              2 ≥ 2? YES → Risk = MEDIUM
```

**Result:** `"medium"`

---

### STEP 10 — Backend Looks Up Medicines and Advice

**Component responsible:** ⑤ Result Builder (Part B)

```
Predicted disease: "Hypertension"
                    ↓
        Search medicine_db.json
    for key = "Hypertension"
                    ↓
            ┌── FOUND ──┐
            │            │
     Medicines:          Advice:
     • Amlodipine 5mg    • Monitor BP regularly
     • Lisinopril 10mg   • Reduce sodium
     • Losartan 50mg     • Exercise 30 min/day
                         • Manage stress
```

If the disease is NOT found in the database, the system returns:
- Medicines: `[]` (empty)
- Advice: `["Please consult a qualified healthcare professional for personalized guidance."]`

---

### STEP 11 — Backend Sends the Complete Result Back

**Component responsible:** ⑤ Result Builder (Part C)

The server assembles everything into a single JSON response and sends it back to the browser with a `200 OK` status:

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
    {"name": "Lisinopril", "dosage": "10mg once daily"},
    {"name": "Losartan", "dosage": "50mg once daily"}
  ],
  "advice": [
    "Monitor blood pressure regularly",
    "Reduce sodium intake",
    "Exercise 30 minutes daily",
    "Manage stress through relaxation techniques"
  ]
}
```

The server also logs this request internally (method, path, status code, response time) for monitoring.

---

### STEP 12 — Frontend Displays the Result

The browser receives the JSON response. The frontend JavaScript:
1. Hides the loading spinner
2. Re-enables the submit button
3. Shows the results section with:
   - **Primary disease** with its confidence score (e.g., "Hypertension — 87% confidence")
   - **Risk level badge** color-coded (green = low, yellow = medium, red = high)
   - **Confidence visualization** (a progress bar or meter)
   - **Top 5 diseases** ranked by probability
   - **Medicine recommendations** with dosages
   - **Lifestyle & clinical advice** as a list
   - **Medical disclaimer** reminding users to consult a real doctor

---

### STEP 13 — User Reads the Result

The user reviews all the information displayed. They now have:
- A preliminary idea of what condition their symptoms suggest
- How confident the system is
- Whether the situation seems low, medium, or high risk
- What medicines are commonly associated with the condition
- What lifestyle changes could help

---

### STEP 14 — User Decides What to Do Next

The user has three options:

| Option | What happens |
|---|---|
| **Try again** | Scroll up, change inputs, click "Predict" again → repeat from Step 3 |
| **Browse other pages** | Click "About" or "Contact" in the navigation → Flask serves a different HTML page |
| **Close the page** | Close the browser tab → session ends, nothing is stored |

> **Note:** The system does not store any user data. There are no accounts, no saved histories, no cookies with health data. Each prediction is independent.

---

## 5. How the Components Interact — The Order of Operations

This diagram shows the exact sequence of communication between every component, from request to response:

```
  USER                  FRONTEND              FLASK SERVER (app.py)
   │                      │                          │
   │  Opens website       │                          │
   │─────────────────────>│  GET /                   │
   │                      │─────────────────────────>│
   │                      │     index.html           │
   │                      │<─────────────────────────│
   │  Sees the form       │                          │
   │<─────────────────────│                          │
   │                      │                          │
   │  Fills form + clicks │                          │
   │  "Predict"           │                          │
   │─────────────────────>│                          │
   │                      │  POST /predict {JSON}    │
   │                      │─────────────────────────>│
   │                      │                          │
   │                      │            ┌─────────────┴──────────────┐
   │                      │            │                            │
   │                      │            │  ② VALIDATE INPUT          │
   │                      │            │  Is everything correct?    │
   │                      │            │                            │
   │                      │            │  If NO → return 400 error  │
   │                      │            │  If YES ↓                  │
   │                      │            │                            │
   │                      │            │  ③ SCALE FEATURES          │
   │                      │            │  scaler.pkl transforms     │
   │                      │            │  age, bp, cholesterol      │
   │                      │            │          ↓                 │
   │                      │            │                            │
   │                      │            │  ④ RUN MODEL               │
   │                      │            │  best_model.pkl predicts   │
   │                      │            │  disease_encoder decodes   │
   │                      │            │          ↓                 │
   │                      │            │                            │
   │                      │            │  ⑤ BUILD RESULT            │
   │                      │            │  Calculate risk level      │
   │                      │            │  Look up medicines         │
   │                      │            │  Assemble JSON response    │
   │                      │            │                            │
   │                      │            └─────────────┬──────────────┘
   │                      │                          │
   │                      │    200 OK {result JSON}  │
   │                      │<─────────────────────────│
   │                      │                          │
   │  Sees disease,       │                          │
   │  risk, medicines,    │                          │
   │  and advice          │                          │
   │<─────────────────────│                          │
   │                      │                          │
```

**Key point:** Everything in the gray box (②→③→④→⑤) happens inside a single HTTP request. The user waits less than 500 milliseconds. There are no background jobs, no queues, no databases to query. It is one request in, one response out.

---

## 6. How User Input Is Processed

Here is a concrete example tracing one piece of user input — **age = 45** — through the entire system:

```
Stage 1: User types "45" into the Age field on the web form.

Stage 2: Frontend collects it as {"age": 45} in the JSON body.

Stage 3: Input Validator checks:
         ✓ Is it a number? Yes.
         ✓ Is it between 0 and 120? Yes.
         → PASS

Stage 4: Feature Preprocessor takes age = 45 and runs:
         scaler.transform([[45, ...]]) → age_scaled = -0.23
         (The scaler knows the mean and standard deviation from training data
          and applies the formula: scaled = (value - mean) / std_dev)

Stage 5: Prediction Engine receives age_scaled = -0.23 as part of the
         input DataFrame. The model uses this scaled value (not 45) to
         compute disease probabilities.

Stage 6: Result Builder uses the raw age = 45 (not scaled) to calculate
         risk level: "Is age > 60?" → No.
```

**Important distinction:**
- The **ML model** sees the **scaled** value (`-0.23`)
- The **risk calculator** sees the **raw** value (`45`)
- These are two different uses of the same input, handled by different components

---

## 7. How Tasks Are Tracked and Completed

### 7.1 — What "Tasks" Mean in This System

In MediCare AI, a "task" is a single prediction request. Unlike a project management tool, this system doesn't have long-running tasks. Each task is:
- **Created** when the user clicks "Predict"
- **Completed** when the response is displayed (typically within 500ms)
- **Independent** — it has no connection to any previous or future prediction

### 7.2 — Task Lifecycle

Every prediction goes through these states internally:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   RECEIVED   │────>│  PROCESSING  │────>│  COMPLETED   │
│              │     │              │     │              │
│ POST /predict│     │ Validate     │     │ 200 OK       │
│ arrives      │     │ Scale        │     │ Result JSON  │
│              │     │ Predict      │     │ returned     │
│              │     │ Build result │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            │ (if validation fails)
                            ▼
                     ┌──────────────┐
                     │   REJECTED   │
                     │              │
                     │ 400 Error    │
                     │ with reasons │
                     └──────────────┘
```

### 7.3 — How the System Knows Each Step Completed

Each internal step has a built-in check:

| Step | Check | What happens if it fails |
|---|---|---|
| Input validation | All 8 fields pass type/range checks | Return `400` with specific errors |
| Feature scaling | Scaler transforms without errors | Return `500` with logged error |
| Model prediction | `predict_proba()` returns valid probabilities | Return `500` with logged error |
| Label decoding | Disease index maps to a known name | Use "Unknown" as fallback |
| Medicine lookup | Disease name found in database | Use generic fallback advice |
| Response assembly | JSON is well-formed | Caught by Flask's JSON serializer |

### 7.4 — Logging — The System's Record Keeper

Every request is logged with:

```
2026-06-15 14:32:07 [INFO] medicare: POST /predict — 200 — 127ms
2026-06-15 14:32:07 [INFO] medicare: Predicted "Hypertension" (confidence: 0.87, risk: medium)
```

If something goes wrong:

```
2026-06-15 14:33:12 [ERROR] medicare: POST /predict — 400 — Validation failed: age=-5 (out of range 0-120)
2026-06-15 14:35:44 [ERROR] medicare: POST /predict — 500 — Model inference failed
    Traceback (most recent call last):
      ...
```

Logs are written using Python's `logging` module (never `print()`), with timestamps and severity levels so they can be monitored in production.

---

## 8. How Success Is Confirmed

### 8.1 — Per-Request Success (Real-Time)

For every single prediction request, the system confirms success by verifying:

```
✓ CHECKPOINT 1: Input is valid
  → All 8 fields present, correct type, within allowed range

✓ CHECKPOINT 2: Preprocessing completed
  → Scaler produced 3 scaled values without NaN or Inf

✓ CHECKPOINT 3: Model produced a prediction
  → predict_proba() returned an array of probabilities that sum to ~1.0

✓ CHECKPOINT 4: Disease name resolved
  → Label encoder mapped the predicted index to a real disease name

✓ CHECKPOINT 5: Response is complete
  → JSON contains all required fields: disease, confidence, risk, top5, medicines, advice

  ALL PASSED → Send 200 OK to user
```

If any checkpoint fails, the system:
1. Logs the error with full details
2. Returns an appropriate error response (`400` or `500`)
3. Shows a user-friendly error message on the frontend (not raw technical text)

### 8.2 — System-Level Success (Operational Health)

Beyond individual requests, the system confirms it's healthy through:

| Mechanism | How it works | Frequency |
|---|---|---|
| `/health` endpoint | Returns `{"status": "healthy"}` if all models are loaded | On demand / Docker healthcheck every 30s |
| `/models` endpoint | Returns model metadata (type, version, disease count) | On demand |
| Startup verification | Logs confirm all 4 artifacts loaded: model, encoder, scaler, medicine DB | Once at boot |
| Request logging | Every request logged with status and duration | Every request |

### 8.3 — Long-Term Success (Quality Gates)

Before the project is declared "done," these gates must pass:

| Gate | Criteria |
|---|---|
| **Prediction correctness** | ≥ 3 out of 5 known test cases return the correct disease |
| **Test coverage** | `pytest` achieves ≥ 80% line coverage on `app.py` |
| **Feature alignment** | Scaler is loaded and applied; lines 433–448 of old code are deleted |
| **Code quality** | `ruff check .` passes with zero errors; zero `print()` statements |
| **Containerization** | `docker build` succeeds; container starts; `/health` returns 200 |
| **Documentation** | README enables a new developer to run the project unassisted |

---

## 9. What Happens When Something Goes Wrong

The system handles four types of failures:

### Failure Type 1 — Bad User Input

```
User sends: {"age": -5, "gender": 3}

System response:
  HTTP 400 Bad Request
  {
    "error": "Validation failed",
    "details": [
      "age must be between 0 and 120 (received: -5)",
      "gender must be 0 or 1 (received: 3)"
    ]
  }

Frontend shows:
  "Please fix the following errors:
   • Age must be between 0 and 120
   • Gender must be male or female"
```

**Impact:** Only the current request fails. The system stays healthy.

---

### Failure Type 2 — Model Not Loaded

```
Server starts but best_model.pkl is missing or corrupt.

System behavior:
  - Startup log: "[ERROR] Failed to load model: FileNotFoundError"
  - /health returns: 200 (app is running) but with degraded status
  - /predict returns: HTTP 500
    {"error": "Prediction service unavailable. Please try again later."}

Frontend shows:
  "The prediction service is temporarily unavailable. Please try again later."
```

**Impact:** All prediction requests fail until the model is restored. Health check reveals the problem.

---

### Failure Type 3 — Unknown Disease (No Medicine Entry)

```
Model predicts: "Rare Condition X"
medicine_db.json has no entry for "Rare Condition X"

System behavior:
  - Returns the prediction normally (disease name + confidence + risk)
  - Medicines: [] (empty)
  - Advice: ["Please consult a qualified healthcare professional
              for personalized guidance on this condition."]

Frontend shows:
  Everything as normal, but the medicines section says:
  "No specific medicine recommendations available.
   Please consult your healthcare provider."
```

**Impact:** None. The prediction still works. The user just gets generic advice instead of specific medicines.

---

### Failure Type 4 — Unexpected Server Error

```
Something completely unexpected crashes during processing.

System behavior:
  - Logger captures the full stack trace
  - Returns: HTTP 500
    {"error": "An unexpected error occurred. Please try again."}
  - No sensitive information (file paths, code) is leaked to the user

Frontend shows:
  "Something went wrong. Please try again. If the problem persists,
   contact support."
```

**Impact:** Only the current request fails. The system logs the error for debugging.

---

## 10. The Complete System Map

This is the full picture of every file, artifact, and connection in the system:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MediCare AI System                             │
│                                                                         │
│  ┌─── Configuration ────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  config.py ◄──── .env (secrets, paths, port)                    │   │
│  │      │            .env.example (template for .env)               │   │
│  │      │                                                           │   │
│  └──────┼───────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌─── Application Core ────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  app.py (Flask Server)                                          │   │
│  │    │                                                             │   │
│  │    ├── Route: GET /          → serves index.html                │   │
│  │    ├── Route: GET /about     → serves about.html                │   │
│  │    ├── Route: GET /contact   → serves contact.html              │   │
│  │    ├── Route: GET /health    → returns system status             │   │
│  │    ├── Route: GET /models    → returns model metadata            │   │
│  │    └── Route: POST /predict  → the main prediction pipeline:    │   │
│  │         │                                                        │   │
│  │         ├── 1. validate_input()                                  │   │
│  │         ├── 2. scaler.transform()  ◄── scaler.pkl               │   │
│  │         ├── 3. model.predict_proba() ◄── best_model.pkl         │   │
│  │         ├── 4. encoder.inverse_transform() ◄── disease_encoder  │   │
│  │         ├── 5. calculate_risk_level()                            │   │
│  │         └── 6. lookup_medicines() ◄── medicine_db.json          │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─── Frontend ─────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  templates/                                                      │   │
│  │    ├── index.html    (form + results display)                   │   │
│  │    ├── about.html    (system information)                       │   │
│  │    └── contact.html  (contact details)                          │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─── ML Artifacts (loaded once at startup) ────────────────────────┐   │
│  │                                                                  │   │
│  │  best_model.pkl        Trained scikit-learn classifier           │   │
│  │  disease_encoder.pkl   Label encoder (index → disease name)      │   │
│  │  scaler.pkl            Feature scaler (age, BP, cholesterol)     │   │
│  │  medicine_db.json      Medicine & advice knowledge base          │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─── Data ────────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  Cleaned_Dataset.csv   Training data (used offline only)        │   │
│  │  data/schema.md        Data contract documenting the CSV        │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─── DevOps & Quality ────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  Dockerfile            [PLANNED — Not yet created]               │   │
│  │  docker-compose.yml    [PLANNED — Not yet created]               │   │
│  │  .dockerignore         [PLANNED — Not yet created]               │   │
│  │  .gitignore            ✅ Present                                │   │
│  │  .github/workflows/    [PLANNED — Not yet created]               │   │
│  │  pyproject.toml        [PLANNED — Not yet created]               │   │
│  │  requirements.txt      ✅ Present                                │   │
│  │  requirements-dev.txt  [PLANNED — Not yet created]               │   │
│  │  tests/                ✅ Present (57 tests passing)             │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─── Documentation ───────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  README.md             Setup guide, architecture, API examples   │   │
│  │  docs/api.md           [PLANNED — Not yet created]               │   │
│  │  documentations/       Planning docs (PRD, claude.md, etc.)     │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Key Rules the Architecture Must Follow

These rules come directly from the source documents and are **non-negotiable**. Every design decision in this architecture plan obeys them.

### Rule 1 — Feature Scaling Must Match Training
> The scaler used at serving time (`scaler.pkl`) must be the **exact same object** that was fit during model training. Raw values must never be passed to the model.

### Rule 2 — No Hardcoded Configuration
> All file paths, port numbers, and settings must come from `config.py` / `.env`. The code should work in any directory, any server, any container without editing source files.

### Rule 3 — Graceful Degradation
> The app must not crash if `medicine_database.pkl` is missing. Fallback logic must be preserved. Only the model itself (`best_model.pkl`) is truly required for core functionality.

### Rule 4 — No Print Statements
> All logging uses Python's `logging` module. `print()` is forbidden in production code.

### Rule 5 — Validate Before Processing
> User input is always validated before any processing begins. Invalid data never reaches the scaler or the model.

### Rule 6 — No Data Leaks in Errors
> Error responses to users must be friendly and generic. Stack traces, file paths, and model internals are logged server-side only.

### Rule 7 — Stateless Requests
> Each prediction request is completely independent. The server stores nothing about the user or their previous predictions.

---

## 12. Summary — The Architecture in 60 Seconds

```
MediCare AI is a single-page medical prediction tool.

It has 6 components:
  ① A frontend (3 HTML pages)
  ② An input validator
  ③ A feature scaler
  ④ An ML prediction model
  ⑤ A result builder (risk + medicines + advice)
  ⑥ A configuration manager

The user journey is 14 steps:
  Open page → Fill form → Click predict → Validate → Scale → Predict
  → Calculate risk → Look up medicines → Send result → Display → Done

Everything happens in one HTTP request (<500ms).
No accounts. No stored data. No background jobs.

The system confirms success at 5 checkpoints:
  Valid input → Good scaling → Valid prediction → Disease resolved → Complete response

If anything fails, the user gets a clear error message.
The server logs the technical details for debugging.

The architecture guarantees:
  • Predictions use properly scaled features (not raw values)
  • All settings are externalized (nothing hardcoded)
  • Every request is validated before processing
  • Every error is handled gracefully
  • The system is containerized and tested (≥80% coverage)

Pending Implementation:
The following items from the System Map are currently pending implementation:
- Containerization: Dockerfile, docker-compose.yml, .dockerignore
- CI/CD automation: .github/workflows/ workflows
- Linting utilities: pyproject.toml configuration for Ruff
- Documentation: docs/api.md
- Dependencies configuration: requirements-dev.txt
```

---

> **Document Status:** Complete v1.0  
> **Related Documents:** [PRD.md](file:///c:/Users/deepa/Downloads/NEW%20PROJECT/documentations/PRD.md) · [claude.md](file:///c:/Users/deepa/Downloads/NEW%20PROJECT/documentations/claude.md) · [plansdaybyday.md](file:///c:/Users/deepa/Downloads/NEW%20PROJECT/documentations/plansdaybyday.md) · [AGENT_PROMPT.md](file:///c:/Users/deepa/Downloads/NEW%20PROJECT/documentations/AGENT_PROMPT.md)
