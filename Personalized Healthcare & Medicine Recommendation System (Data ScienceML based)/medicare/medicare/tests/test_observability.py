import logging


def test_metrics_endpoint(app_client):
    response = app_client.get("/metrics")
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert b"medicare_requests_total" in response.data

def test_metrics_increment_after_request(app_client):
    before = app_client.get("/metrics").data
    app_client.get("/health")
    after = app_client.get("/metrics").data
    assert after != before


def test_request_logging_avoids_payload_values(app_client, valid_prediction_data, caplog):
    caplog.set_level(logging.INFO)
    response = app_client.post("/predict", json=valid_prediction_data)
    assert response.status_code == 200
    logs = "\n".join(record.getMessage() for record in caplog.records)
    assert "POST /predict" in logs
    assert str(valid_prediction_data.get("age", "")) not in logs
