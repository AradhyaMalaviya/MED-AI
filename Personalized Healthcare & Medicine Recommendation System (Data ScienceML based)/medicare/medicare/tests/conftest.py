# ============================================================================
# conftest.py — Shared Pytest Fixtures for MediCare AI
# ============================================================================
# Provides Flask test client, mock model/encoder/scaler fixtures, and
# common test data helpers used across all test modules.
# ============================================================================

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Ensure the application root is on sys.path so `import app` works
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# ---------- Mock artifacts (model, encoder, scaler) ----------

def _make_mock_model(num_classes=10):
    """Create a mock sklearn model that returns deterministic predictions."""
    mock = MagicMock()
    mock.predict.return_value = np.array([0])

    probs = np.zeros(num_classes)
    probs[0] = 0.85
    probs[1] = 0.05
    probs[2] = 0.03
    probs[3] = 0.02
    probs[4] = 0.02
    remaining = 1.0 - probs.sum()
    for i in range(5, num_classes):
        probs[i] = remaining / (num_classes - 5)
    mock.predict_proba.return_value = np.array([probs])
    return mock


def _make_mock_encoder(num_classes=10):
    """Create a mock LabelEncoder with realistic disease names."""
    mock = MagicMock()
    classes = np.array([
        'Influenza', 'Common Cold', 'Asthma', 'Diabetes',
        'Hypertension', 'Pneumonia', 'Bronchitis', 'Depression',
        'Stroke', 'Anxiety Disorders',
    ])[:num_classes]
    mock.classes_ = classes
    return mock



# ---------- Fixtures ----------

@pytest.fixture()
def mock_model():
    """A mock ML model returning deterministic predictions."""
    return _make_mock_model()


@pytest.fixture()
def mock_encoder():
    """A mock label encoder with 10 disease classes."""
    return _make_mock_encoder()



@pytest.fixture()
def app_client(mock_model, mock_encoder):
    """Flask test client with all ML artifacts mocked out.

    This patches the module-level globals in ``app`` so that tests can
    exercise the HTTP endpoints without needing real ``.pkl`` files.
    """
    # Patch the module-level model objects *before* the client is created.
    # We patch at the module level because Flask views reference these globals.
    with patch.dict("app.__dict__", {
        "best_model": mock_model,
        "label_encoder": mock_encoder,
    }):
        import app as app_module
        app_module.best_model = mock_model
        app_module.label_encoder = mock_encoder

        app_module.app.config["TESTING"] = True
        with app_module.app.test_client() as client:
            yield client


@pytest.fixture()
def valid_prediction_data():
    """A minimal, fully-valid prediction request payload."""
    return {
        'age': 45,
        'gender': 1,
        'fever': 1,
        'cough': 1,
        'fatigue': 0,
        'breathing': 0,
        'bloodPressure': 1,
        'cholesterol': 1,
    }
