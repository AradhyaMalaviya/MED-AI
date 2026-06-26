from unittest.mock import patch

import pytest


def test_predict_success(app_client, valid_prediction_data):
    """Test valid prediction request returns 200 with expected JSON structure."""
    response = app_client.post('/predict', json=valid_prediction_data)

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert "disease" in data
    assert "confidence" in data
    assert "risk" in data
    assert "top5" in data
    assert "medicines" in data
    assert "advice" in data
    assert "model_used" in data
    assert "timestamp" in data

def test_predict_top5_sorted(app_client, valid_prediction_data):
    """Test that top5 is sorted by descending confidence."""
    response = app_client.post('/predict', json=valid_prediction_data)

    assert response.status_code == 200
    data = response.get_json()
    top5 = data["top5"]

    assert len(top5) == 5
    # Check if sorted in descending order
    confidences = [item["confidence"] for item in top5]
    assert confidences == sorted(confidences, reverse=True)

@pytest.mark.parametrize("symptoms,expected_risk", [
    ({"fever": 1, "cough": 1, "fatigue": 1, "breathing": 1, "age": 65}, "high"),  # >=3 symptoms, >60 age
    ({"fever": 1, "cough": 1, "fatigue": 0, "breathing": 0, "age": 30}, "medium"), # 2 symptoms
    ({"fever": 1, "cough": 0, "fatigue": 0, "breathing": 0, "age": 30}, "low"),    # 1 symptom
])
def test_predict_various_symptoms(app_client, valid_prediction_data, symptoms, expected_risk):
    """Test with various symptom combinations to check risk level handling in predictions."""
    req_data = valid_prediction_data.copy()
    req_data.update(symptoms)

    response = app_client.post('/predict', json=req_data)
    assert response.status_code == 200
    data = response.get_json()

    assert data["risk"] == expected_risk

def test_predict_model_not_loaded(app_client, valid_prediction_data):
    """Test model-not-loaded scenario returns 500."""
    with patch("app.best_model", None):
        response = app_client.post('/predict', json=valid_prediction_data)
        assert response.status_code == 500
        data = response.get_json()
        assert data["success"] is False
        assert data["error"] == "Model not loaded"


