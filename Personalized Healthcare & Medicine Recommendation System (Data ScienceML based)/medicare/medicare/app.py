# ============================================================================
# FLASK API BACKEND - Connect ML Models to Website
# Save this as: app.py
# ============================================================================

import json
import logging
import pickle
import sys
import time

import joblib
import numpy as np
import pandas as pd
import sklearn.compose._column_transformer as _sklearn_column_transformer
from flask import Flask, Response, g, jsonify, render_template, request
from flask_cors import CORS
from sklearn.impute import SimpleImputer

import config

# ---------- Logging Configuration ----------
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("medicare")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _walk_estimators(estimator):
    """Yield nested sklearn estimators inside pipelines/column transformers."""
    yield estimator

    for _, child in getattr(estimator, "steps", []):
        yield from _walk_estimators(child)

    for attr in ("transformers", "transformers_"):
        for item in getattr(estimator, attr, []) or []:
            if len(item) < 2:
                continue
            child = item[1]
            if child in ("drop", "passthrough"):
                continue
            yield from _walk_estimators(child)


def patch_sklearn_pickle_compatibility(estimator=None):
    """Support model files saved with scikit-learn 1.6.x on newer sklearn."""
    if not hasattr(_sklearn_column_transformer, "_RemainderColsList"):
        class _RemainderColsList(list):
            pass

        _RemainderColsList.__module__ = _sklearn_column_transformer.__name__
        _sklearn_column_transformer._RemainderColsList = _RemainderColsList

    patched_imputers = 0
    if estimator is not None:
        for nested_estimator in _walk_estimators(estimator):
            if (
                isinstance(nested_estimator, SimpleImputer)
                and not hasattr(nested_estimator, "_fill_dtype")
                and hasattr(nested_estimator, "_fit_dtype")
            ):
                nested_estimator._fill_dtype = nested_estimator._fit_dtype
                patched_imputers += 1

    return patched_imputers

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

metrics = {
    "requests_total": 0,
    "errors_total": 0,
    "prediction_requests_total": 0,
    "prediction_failures_total": 0,
    "request_duration_ms_sum": 0.0,
    "request_duration_ms_count": 0,
}

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

@app.before_request
def start_request_timer():
    g.request_start_time = time.perf_counter()

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

    metrics["requests_total"] += 1
    metrics["request_duration_ms_sum"] += duration_ms
    metrics["request_duration_ms_count"] += 1
    if response.status_code >= 500:
        metrics["errors_total"] += 1

    return response

# ============================================================================
# LOAD ALL MODELS AND DATA
# ============================================================================

logger.info("Loading models...")
logger.info("CWD: %s", config.BASE_DIR)

# ---------- Load best_model.pkl ----------
best_model = None
try:
    patch_sklearn_pickle_compatibility()
    best_model = joblib.load(config.MODEL_PATH)
    patched_imputers = patch_sklearn_pickle_compatibility(best_model)
    if patched_imputers:
        logger.info("Applied sklearn pickle compatibility patch to %d imputer(s)", patched_imputers)
    logger.info("Best model loaded from %s", config.MODEL_PATH)
except Exception as e:
    logger.error("Failed to load best_model.pkl — %s: %s", type(e).__name__, e)

# ---------- Load disease_encoder.pkl ----------
label_encoder = None
try:
    with open(config.ENCODER_PATH, 'rb') as f:
        label_encoder = pickle.load(f)
    logger.info("Label encoder loaded from %s", config.ENCODER_PATH)
except Exception as e:
    logger.error("Failed to load disease_encoder.pkl — %s: %s", type(e).__name__, e)

# ---------- Load scaler.pkl ----------
scaler = None
try:
    scaler = joblib.load(config.SCALER_PATH)
    logger.info("Scaler loaded from %s", config.SCALER_PATH)
    logger.info("Scaler feature_names_in_: %s", list(scaler.feature_names_in_))
except Exception as e:
    logger.error("Failed to load scaler.pkl — %s: %s", type(e).__name__, e)
    logger.warning("Without the scaler, predictions will be mathematically incorrect!")

# ============================================================================
try:
    # Load medicine database
    with open(config.MEDICINE_DB_PATH, 'r', encoding='utf-8') as f:
        medicine_db = json.load(f)
    logger.info("Medicine database loaded from %s", config.MEDICINE_DB_PATH)
except Exception as e:
    logger.error("Failed to load medicine database — %s: %s", type(e).__name__, e)
    logger.warning("Medicine database not found — using default fallback")
    medicine_db = {
        'Influenza': {
            'medicines': [
                '💊 Oseltamivir (Tamiflu) 75mg - Take twice daily for 5 days',
                '💊 Acetaminophen 500mg - Every 6 hours for fever',
                '💊 Ibuprofen 400mg - Every 8 hours for body aches',
                '💧 Increase fluid intake to 8-10 glasses daily'
            ],
            'advice': [
                '🛏️ REST: Get 8-10 hours of sleep per night',
                '💧 HYDRATION: Drink at least 8-10 glasses of water daily',
                '🏠 ISOLATION: Stay home for 7 days',
                '🤧 HYGIENE: Cover mouth when coughing',
                '🌡️ MONITOR: Check temperature twice daily',
                '📞 SEEK HELP: If difficulty breathing develops'
            ]
        }
    }

logger.info("Backend ready!")

# ============================================================================
# API ENDPOINTS
# ============================================================================

def validate_input(data):
    """Validate incoming prediction request data.

    Args:
        data: Dictionary of incoming request JSON data.

    Returns:
        Tuple of (is_valid: bool, errors: list[str]).
    """
    errors = []

    validations = {
        'age': (0, 120),
        'gender': (0, 1),
        'fever': (0, 1),
        'cough': (0, 1),
        'fatigue': (0, 1),
        'breathing': (0, 1),
        'bloodPressure': (0, 2),
        'cholesterol': (0, 2)
    }

    for field, (min_val, max_val) in validations.items():
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
            continue

        try:
            val = int(data[field])
            if not (min_val <= val <= max_val):
                errors.append(f"Field '{field}' must be between {min_val} and {max_val}.")
        except (ValueError, TypeError):
            errors.append(f"Field '{field}' must be an integer.")

    return len(errors) == 0, errors


def calculate_risk_level(symptom_count, age, blood_pressure):
    """Calculate patient risk level based on symptoms, age, and blood pressure.

    Business rules:
        - HIGH:   symptom_count >= 3 AND (age > 60 OR blood_pressure == 2)
        - MEDIUM: symptom_count >= 2
        - LOW:    otherwise

    Args:
        symptom_count: Number of active symptoms (0–4).
        age: Patient age in years.
        blood_pressure: Encoded blood pressure level (0=Low, 1=Normal, 2=High).

    Returns:
        Risk level string: ``"High"``, ``"Medium"``, or ``"Low"``.
    """
    if symptom_count >= 3 and (age > 60 or blood_pressure == 2):
        return "High"
    elif symptom_count >= 2:
        return "Medium"
    else:
        return "Low"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': best_model is not None,
        'encoder_loaded': label_encoder is not None,
        'scaler_loaded': scaler is not None,
        'medicine_db_loaded': bool(medicine_db),
        'message': 'Backend is running!'
    })

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({
        'available_models': ['rf', 'gb', 'lr'],
        'current_model': 'best_model',
        'diseases_count': len(label_encoder.classes_) if label_encoder else 0
    })

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

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Main prediction endpoint"""

    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        # Get data from request
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'message': 'Please send JSON data'
            }), 400

        is_valid, errors = validate_input(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Validation Error',
                'message': 'Invalid input data',
                'details': errors
            }), 400

        metrics["prediction_requests_total"] += 1
        logger.info("Received prediction request")

        # Extract features with defaults
        fever = int(data.get('fever', 0))
        cough = int(data.get('cough', 0))
        fatigue = int(data.get('fatigue', 0))
        difficulty_breathing = int(data.get('breathing', 0))
        age = int(data.get('age', 30))
        gender = int(data.get('gender', 0))
        blood_pressure = int(data.get('bloodPressure', 1))
        cholesterol = int(data.get('cholesterol', 1))
        model_choice = data.get('model', 'rf')

        logger.info("Patient: Age %d, Gender %s", age, 'M' if gender else 'F')
        logger.info("Symptoms: Fever=%d, Cough=%d, Fatigue=%d, Breathing=%d",
                     fever, cough, fatigue, difficulty_breathing)

        # Check if model is loaded
        if best_model is None:
            metrics["prediction_failures_total"] += 1
            return jsonify({
                'success': False,
                'error': 'Model not loaded',
                'message': 'ML model files not found. Please ensure .pkl files are in the correct location.'
            }), 500

        # Check if scaler is loaded
        if scaler is None:
            metrics["prediction_failures_total"] += 1
            return jsonify({
                'success': False,
                'error': 'Scaler not loaded',
                'message': 'scaler.pkl not found. Cannot produce correct predictions without it.'
            }), 500

        # Calculate risk level (needed as model input feature)
        symptom_count = fever + cough + fatigue + difficulty_breathing
        risk_level_str = calculate_risk_level(symptom_count, age, blood_pressure)

        # Prepare input for prediction — match exact training data format
        input_dict = {
            'fever': ['Yes' if fever else 'No'],
            'cough': ['Yes' if cough else 'No'],
            'fatigue': ['Yes' if fatigue else 'No'],
            'difficulty_breathing': ['Yes' if difficulty_breathing else 'No'],
            'age': [age],
            'gender': ['male' if gender == 1 else 'female'],
            'blood_pressure': [blood_pressure],
            'cholesterol_level': [cholesterol],
            'outcome_variable': ['Positive' if symptom_count >= 2 else 'Negative'],
            'risk_level': [risk_level_str],
        }

        input_df = pd.DataFrame(input_dict)

        # Apply the scaler to produce correctly scaled features
        scaled_cols = ["age", "blood_pressure", "cholesterol_level"]
        scaled_values = scaler.transform(input_df[scaled_cols])
        input_df[["age_scaled", "bp_scaled", "chol_scaled"]] = scaled_values

        logger.info("Input DataFrame columns: %s", list(input_df.columns))
        logger.info("Input DataFrame shape: %s", input_df.shape)

        # Make prediction
        prediction = best_model.predict(input_df)[0]
        probabilities = best_model.predict_proba(input_df)[0]

        # Get disease name
        predicted_disease = label_encoder.classes_[prediction]
        main_confidence = float(probabilities[prediction] * 100)

        logger.info("Prediction: %s (%.1f%%)", predicted_disease, main_confidence)

        # Get top 5 predictions
        top_5_idx = np.argsort(probabilities)[-5:][::-1]
        top_5_predictions = []

        for idx in top_5_idx:
            disease_name = label_encoder.classes_[idx]
            confidence = float(probabilities[idx] * 100)
            top_5_predictions.append({
                'disease': disease_name,
                'confidence': round(confidence, 2)
            })

        # Use the risk level already computed for the model input
        risk_level = risk_level_str.lower()

        logger.info("Risk Level: %s", risk_level.upper())

        # Get treatment info
        treatment = medicine_db.get(predicted_disease, {
            'medicines': ['⚕️ Consult doctor for specific treatment'],
            'advice': ['📞 Schedule appointment with healthcare provider']
        })

        # Return response
        response = {
            'success': True,
            'disease': predicted_disease,
            'confidence': round(main_confidence, 2),
            'risk': risk_level,
            'top5': top_5_predictions,
            'medicines': treatment.get('medicines', []),
            'advice': treatment.get('advice', []),
            'model_used': model_choice,
            'timestamp': pd.Timestamp.now().isoformat()
        }

        logger.info("Sending response for disease: %s", predicted_disease)

        return jsonify(response), 200

    except Exception:
        metrics["prediction_failures_total"] += 1
        logger.exception("Prediction failed")

        return jsonify({
            'success': False,
            'error': 'Prediction failed',
            'message': 'Prediction failed. Please try again later.'
        }), 500

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("MEDICARE AI — BACKEND SERVER")
    logger.info("=" * 60)
    logger.info("Server starting...")
    logger.info("API will be available at: http://localhost:%d", config.PORT)
    logger.info("Frontend should connect to: http://localhost:%d/predict", config.PORT)
    logger.info("To test: Send POST request to /predict endpoint")
    logger.info("=" * 60)

    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
