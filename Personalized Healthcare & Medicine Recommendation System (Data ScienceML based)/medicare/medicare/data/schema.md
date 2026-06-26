# Dataset Schema (`Cleaned_Dataset.csv`)

This document describes the exact schema of the `Cleaned_Dataset.csv` file used to train the machine learning models. This schema serves as the data contract for any future model retraining.

## Columns

| Column Name | Data Type | Allowed Values / Range | Description |
| :--- | :--- | :--- | :--- |
| `disease` | String | Various disease names (e.g., 'Influenza', 'Asthma') | The target label representing the diagnosed disease. |
| `fever` | String | `'Yes'`, `'No'` | Indicates whether the patient has a fever. |
| `cough` | String | `'Yes'`, `'No'` | Indicates whether the patient has a cough. |
| `fatigue` | String | `'Yes'`, `'No'` | Indicates whether the patient experiences fatigue. |
| `difficulty_breathing` | String | `'Yes'`, `'No'` | Indicates whether the patient has difficulty breathing. |
| `age` | Integer | `0`–`120` (typical human age range) | The age of the patient in years. |
| `gender` | String | `'male'`, `'female'` | The gender of the patient. |
| `blood_pressure` | Integer | `0`, `1`, `2` | Encoded blood pressure level (e.g., 0=Low, 1=Normal, 2=High). |
| `cholesterol_level` | Integer | `0`, `1`, `2` | Encoded cholesterol level (e.g., 0=Low, 1=Normal, 2=High). |
| `outcome_variable` | String | `'Positive'`, `'Negative'` | (Training-data only artifact, not a model input). Outcome indicator based on symptoms. |
| `age_scaled` | Float | Unbounded | (Training-data only artifact). The standard-scaled version of `age`. |
| `bp_scaled` | Float | Unbounded | (Training-data only artifact). The standard-scaled version of `blood_pressure`. |
| `chol_scaled` | Float | Unbounded | (Training-data only artifact). The standard-scaled version of `cholesterol_level`. |
| `risk_level` | String | `'Low'`, `'Medium'`, `'High'` | (Training-data only artifact, not a model input). The computed risk level of the patient based on symptoms and vitals. |

## Notes for API Preprocessing

The API `/predict` endpoint receives inputs numerically for some categorical features:
- **Symptoms** (fever, cough, fatigue, difficulty_breathing): `1` (Yes), `0` (No)
- **Gender**: `1` (Male), `0` (Female)
- **Blood Pressure & Cholesterol**: Passed as `0`, `1`, `2`

The API transforms these raw values back into the text representations (e.g., `'Yes'`, `'No'`, `'male'`, `'female'`) expected by the pre-trained `best_model.pkl` pipeline. Scaling operations are handled natively within the `best_model.pkl` inference pipeline.
