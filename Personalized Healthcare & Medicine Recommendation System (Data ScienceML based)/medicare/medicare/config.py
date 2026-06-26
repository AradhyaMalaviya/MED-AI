# ============================================================================
# CONFIGURATION MODULE — Externalized Settings for MediCare AI
# ============================================================================
# All hardcoded paths and settings are centralized here.
# Values can be overridden via environment variables or a .env file.
# ============================================================================

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Base directory — resolves to the directory containing this config file
BASE_DIR = Path(__file__).resolve().parent

# ---------- Model / Artifact Paths ----------
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE_DIR / "best_model.pkl")))
ENCODER_PATH = Path(os.getenv("ENCODER_PATH", str(BASE_DIR / "disease_encoder.pkl")))
MEDICINE_DB_PATH = Path(os.getenv("MEDICINE_DB_PATH", str(BASE_DIR / "medicine_db.json")))
SCALER_PATH = Path(os.getenv("SCALER_PATH", str(BASE_DIR / "scaler.pkl")))

# ---------- Server Settings ----------
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
ALLOWED_ORIGINS = [orig.strip() for orig in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

# ---------- Observability ----------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "local")
