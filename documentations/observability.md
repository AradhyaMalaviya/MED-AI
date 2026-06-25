# Observability and Monitoring

## Metrics Endpoint

Metrics are available at:
```
GET /metrics
```

You can test this locally:
```powershell
curl.exe http://localhost:5000/metrics
```

## Suggested Alert Thresholds

| Signal | Suggested alert |
|---|---|
| Container healthcheck failing | Alert immediately after 3 consecutive failures. |
| HTTP 5xx rate | Alert if 5xx responses exceed 5% for 5 minutes. |
| Prediction failures | Alert if failures exceed 3 consecutive requests. |
| Average request duration | Alert if average exceeds 1000ms for 10 minutes. |
| Sentry errors | Alert on new unhandled exception type. |

## Suggested Dashboard Panels

| Panel | Source |
|---|---|
| Total requests | `medicare_requests_total` |
| 5xx errors | `medicare_errors_total` |
| Prediction requests | `medicare_prediction_requests_total` |
| Prediction failures | `medicare_prediction_failures_total` |
| Average latency | `medicare_request_duration_ms_avg` |
| Container health | Docker healthcheck and `/health` |

## CI Limitation for Models

The `.pkl` artifacts are intentionally ignored by Git. Therefore, the Docker image built in GitHub Actions CI currently lacks the loaded models.
**Unresolved Artifact Strategy**: A strategy needs to be implemented for CI (such as downloading release assets, using Git LFS, or pulling from cloud storage) before we can require a real model-loaded container smoke test in the CI pipeline.
