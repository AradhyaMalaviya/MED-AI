# MediCare AI API Specifications

This document outlines the public REST API contracts, request payloads, response schemas, and error states for the MediCare AI backend.

---

## Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---:|
| `POST` | `/predict` | Consumes clinical variables, scales inputs, runs model inference, and returns disease/treatment. | No |
| `GET` | `/health` | Liveness & readiness checker detailing application loading states. | No |
| `GET` | `/models` | Exposes metadata for loaded models and output disease classes count. | No |

---

## 1. POST /predict

### Description
Consumes raw clinical patient vitals and symptom arrays, applies standard feature scaling normalization, triggers machine learning prediction inference, maps the classified output to the clinical recommendation database, and computes urgency risk metrics.

### Headers
```http
Content-Type: application/json
```

### JSON Request Schema Contract

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PredictRequest",
  "type": "OBJECT",
  "properties": {
    "age": {
      "type": "INTEGER",
      "minimum": 0,
      "maximum": 120,
      "description": "Patient age in years."
    },
    "gender": {
      "type": "INTEGER",
      "enum": [0, 1],
      "description": "Patient gender: 0 = Female, 1 = Male."
    },
    "fever": {
      "type": "INTEGER",
      "enum": [0, 1],
      "description": "Fever trigger status: 0 = Absent, 1 = Present."
    },
    "cough": {
      "type": "INTEGER",
      "enum": [0, 1],
      "description": "Cough trigger status: 0 = Absent, 1 = Present."
    },
    "fatigue": {
      "type": "INTEGER",
      "enum": [0, 1],
      "description": "Fatigue trigger status: 0 = Absent, 1 = Present."
    },
    "breathing": {
      "type": "INTEGER",
      "enum": [0, 1],
      "description": "Difficulty breathing trigger status: 0 = Absent, 1 = Present."
    },
    "bloodPressure": {
      "type": "INTEGER",
      "enum": [0, 1, 2],
      "description": "Systolic/diastolic blood pressure tier: 0 = Low, 1 = Normal, 2 = High."
    },
    "cholesterol": {
      "type": "INTEGER",
      "enum": [0, 1, 2],
      "description": "Serum cholesterol tier: 0 = Low, 1 = Normal, 2 = High."
    },
    "model": {
      "type": "STRING",
      "enum": ["rf", "gb", "lr"],
      "default": "rf",
      "description": "Model architecture selection (Random Forest, Gradient Boosting, or Logistic Regression)."
    }
  },
  "required": ["age", "gender", "fever", "cough", "fatigue", "breathing", "bloodPressure", "cholesterol"]
}
```

### Response Schemes

#### Success Response (200 OK)
Returns prediction classification details, confidence percentages, computed risk levels, top 5 differential diagnoses sorted by probability, recommended drugs with dosages, and lifestyle advice.

```json
{
  "success": true,
  "disease": "Hypertension",
  "confidence": 87.23,
  "risk": "medium",
  "top5": [
    {
      "disease": "Hypertension",
      "confidence": 87.23
    },
    {
      "disease": "Diabetes",
      "confidence": 6.11
    },
    {
      "disease": "Stroke",
      "confidence": 3.42
    },
    {
      "disease": "Bronchitis",
      "confidence": 2.11
    },
    {
      "disease": "Asthma",
      "confidence": 1.13
    }
  ],
  "medicines": [
    "💊 Lisinopril 10mg - Take once daily in the morning",
    "💊 Amlodipine 5mg - Take once daily",
    "💊 Hydrochlorothiazide 12.5mg - Take once daily in the morning"
  ],
  "advice": [
    "🍎 DIET: Follow the DASH diet (high in fruits/vegetables, low in sodium)",
    "🏃 EXERCISE: Participate in 150 minutes of moderate aerobic activity weekly",
    "🚭 HABITS: Limit alcohol intake and avoid smoking",
    "🌡️ MONITOR: Record blood pressure twice daily (morning and evening)"
  ],
  "model_used": "rf",
  "timestamp": "2026-06-25T15:47:00.123456"
}
```

#### Client Validation Error (400 Bad Request)
Returned when payload parameters are missing, have incorrect types, or lie outside expected ranges.

```json
{
  "success": false,
  "error": "Validation Error",
  "message": "Invalid input data",
  "details": [
    "Field 'age' must be between 0 and 120.",
    "Field 'bloodPressure' must be between 0 and 2."
  ]
}
```

#### Server Error (500 Internal Server Error)
Returned when the server encounters unexpected failures such as serialized model reading exceptions or scaler compatibility blockages.

```json
{
  "success": false,
  "error": "Prediction failed",
  "message": "Prediction failed. Please try again later."
}
```

---

## 2. GET /health

### Description
Provides operational health reporting for load balancers and container orchestration platforms (like Kubernetes or ECS). Ensures that all necessary inference artifacts (ML model, label encoder, and medicine database) are loaded successfully in memory.

### Success Response (200 OK)
```json
{
  "status": "healthy",
  "model_loaded": true,
  "encoder_loaded": true,
  "medicine_db_loaded": true,
  "message": "Backend is running!"
}
```

### Degraded Response (500 Internal Server Error)
Exposed if the server process is alive but one or more critical machine learning serialization files are corrupted or missing from the disk.

```json
{
  "status": "degraded",
  "model_loaded": false,
  "encoder_loaded": true,
  "medicine_db_loaded": true,
  "message": "Critical dependencies are missing."
}
```

---

## 3. GET /models

### Description
Exposes system-level machine learning configuration parameters, including the default active classification model and the total target category dimension of predicted labels.

### Success Response (200 OK)
```json
{
  "available_models": ["rf", "gb", "lr"],
  "current_model": "best_model",
  "diseases_count": 9
}
```
