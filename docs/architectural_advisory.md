# Beyond Day 10 — Post-Roadmap Architectural Advisory Report

This report provides high-level architectural guidance to address and resolve the remaining open operational questions in the MediCare AI product lifecycle.

---

## 1. Resolution for Q-002: Recommendation Engine Evolution

### Current Approach vs. Hybrid/Deep Learning Trade-Offs
The current implementation utilizes a deterministic dictionary lookup (`medicine_db.json`) mapped directly to the disease category predicted by the Random Forest classifier.

While highly reliable, low-latency ($<1\text{ms}$ database lookup), and easy to maintain, it lacks personalization: every patient diagnosed with "Hypertension" receives the exact same recommendations, regardless of age, vital variations, or behavioral history.

Integrating the advanced hybrid recommendation ideas from `Personalized Reco System.txt` introduces trade-offs:

| Dimension | Current Approach (`medicine_db.json`) | Hybrid / Deep Learning Embeddings Engine |
| :--- | :--- | :--- |
| **Model Complexity** | Negligible (JSON key lookup). | High (TensorFlow neural networks, TF-IDF vectors, Surprise SVD). |
| **Data Requirements** | Static mapping files. | Requires user interaction tracking, reviews, and clinical logs. |
| **Inference Latency** | $<1\text{ms}$. | $50\text{ms} - 250\text{ms}$ depending on model size and retrieval depth. |
| **Personalization** | Cohort level (none). | Individual level (accounts for age, BP levels, drug interactions). |
| **Clinical Validation** | Simple validation of static text mappings. | Risk of non-deterministic recommendations requiring strict guardrails. |

### Phase 2 Architecture: Deep Learning Embeddings Retrieval
To upgrade the engine without breaking the existing Flask REST API, we propose a two-stage **Retrieval-Filtering (Bi-Encoder)** architecture:

```text
                                     ┌────────────────────────────────┐
                                     │   POST /predict Request        │
                                     └───────────────┬────────────────┘
                                                     │
                                                     ▼
                                     ┌────────────────────────────────┐
                                     │  Stage 1: Disease Classifier   │
                                     │  (best_model.pkl - serving)    │
                                     └───────────────┬────────────────┘
                                                     │ Decoded Disease Target
                                                     ▼
                                     ┌────────────────────────────────┐
                                     │  Stage 2: Candidate Retrieval   │
                                     │  Retrieve base treatments and   │
                                     │  lifestyle options from DB     │
                                     └───────────────┬────────────────┘
                                                     │ Mapped Candidates
                                                     ▼
 ┌───────────────────────────┐       ┌────────────────────────────────┐
 │ Patient Context Embeddings│ ───>  │  Stage 3: Deep Learning Ranker  │
 │ (Age, Gender, Vitals      │       │  Compute cosine similarity of  │
 │  vectorized via Keras)    │       │  Candidate & Patient vectors   │
 └───────────────────────────┘       └───────────────┬────────────────┘
                                                     │ Ranked List
                                                     ▼
                                     ┌────────────────────────────────┐
                                     │   Clinical Guardrail Layer     │
                                     │   Check interactions, contra-  │
                                     │   indications, dosage limits   │
                                     └───────────────┬────────────────┘
                                                     │ Verified Output
                                                     ▼
                                     ┌────────────────────────────────┐
                                     │     JSON API Output Response   │
                                     └────────────────────────────────┘
```

1. **Stage 1 (Classification)**: The Random Forest model predicts the primary disease class.
2. **Stage 2 (Candidate Retrieval)**: The system queries a candidate database to fetch a pool of potential treatments and advice mapped to the predicted disease.
3. **Stage 3 (Neural Re-ranking)**:
   * Patient variables and candidate descriptions are mapped into a shared vector space.
   * A lightweight TensorFlow Keras model calculates embeddings for the patient profile (representing their demographic and clinical state) and the treatment candidates.
   * Recommendations are ranked using cosine similarity between patient and treatment embeddings.
4. **Stage 4 (Clinical Safety Filter)**: A hardcoded rule layer screens the ranked candidates for age limits, blood pressure warnings, and drug interactions before returning the final response.

---

## 2. Resolution for Q-003: Target Cloud Infrastructure Strategy

We propose a containerized serverless hosting model on AWS or GCP. This maintains low operational overhead, automates scaling, and secures configuration secrets.

### Option A: Google Cloud Platform (GCP) — Recommended
GCP is selected as the primary target due to its simple container setup and serverless runtime capabilities.

```text
  [DNS - Cloud DNS]
          │
          ▼
  [Load Balancer - Cloud Armor (WAF)]
          │
          ▼
  [Serverless Container - Cloud Run]
     (Runs medicare-ai Docker Image)
          │
          ├─────── Reads Secrets ────────> [Secret Manager]
          │                                (SENTRY_DSN, MODEL_PATH)
          │
          └─────── Exports Metrics ──────> [Cloud Logging / Monitoring]
```

1. **Provisioning (GCP Cloud Run)**:
   * Deploy the Docker image directly to GCP Cloud Run. Cloud Run handles automatic scaling (down to 0 instances to minimize cost) and provides HTTPS endpoints out of the box.
   * CPU allocation: 1 vCPU with 2GB Memory (sufficient for Gunicorn and scikit-learn models).
2. **Configuration & Secrets (GCP Secret Manager)**:
   * Sensitive variables (e.g., `SENTRY_DSN`, production API keys) are stored in Google Cloud Secret Manager.
   * Cloud Run mounts these secrets directly as environment variables at runtime, keeping secrets out of the Docker image and code repositories.
3. **Domain Mapping (Cloud DNS & Load Balancing)**:
   * Map your custom domain to the Cloud Run service via an HTTPS Load Balancer with Cloud Armor enabled for WAF security.

---

### Option B: Amazon Web Services (AWS)
An alternative layout for AWS-centric organizations.

1. **Provisioning (AWS ECS Fargate)**:
   * Deploy the image to AWS ECS running on Fargate (serverless container orchestration).
   * Put the containers behind an Application Load Balancer (ALB) inside private subnets, routing traffic from public subnets through NAT gateways.
2. **Secrets (AWS Systems Manager Parameter Store)**:
   * Store runtime secrets inside Systems Manager Parameter Store or AWS Secrets Manager.
   * ECS Task Definitions reference these parameters to inject them into the container env on startup.
3. **Domain Mapping (Route 53 & ALB)**:
   * Configure AWS Route 53 to map hostnames to the ALB, using ACM (AWS Certificate Manager) to manage SSL certificates.

---

## 3. Resolution for Q-004: Production Monitoring & Observability Budget

To monitor performance and track errors in production, we recommend integrating Sentry and Prometheus metric exporters with the custom middleware created on Day 9.

### 1. Exception Tracking (Sentry Integration)
The application includes guarded Sentry initialization. To activate it in production:
* Set the environment variables `SENTRY_DSN` and `SENTRY_ENVIRONMENT` in Secret Manager.
* Sentry automatically hooks into the Flask request context to capture unhandled errors.

To record manual warnings or log errors without crashing:
```python
import sentry_sdk
from sentry_sdk import capture_exception, capture_message

try:
    # Critical prediction sequence
    prediction = best_model.predict(input_df)[0]
except Exception as e:
    # Log to local logger
    logger.exception("Prediction failed")
    # Send exception metadata to Sentry
    capture_exception(e)
    # Return user-friendly response
```

### 2. Metrics Aggregation
The `/metrics` endpoint exposes Prometheus-formatted statistics. To set up monitoring:
1. **Prometheus Agent**: Configure a Prometheus server or OpenTelemetry Collector to scrape the application's `/metrics` endpoint every 15-30 seconds.
2. **Secure Access**: In production, restrict access to `/metrics` so it is only reachable by the metrics scraper. This can be configured at the load balancer layer or via internal VPC networks.
3. **Grafana Visualization**: Create dashboard panels using the exported metrics to monitor performance:
   * **Traffic Rate**: `rate(medicare_requests_total[5m])`
   * **Error Rates**: `rate(medicare_errors_total[5m]) / rate(medicare_requests_total[5m])`
   * **Latencies**: `medicare_request_duration_ms_avg`
   * **Model Health**: Alert if `medicare_prediction_failures_total` increases.
