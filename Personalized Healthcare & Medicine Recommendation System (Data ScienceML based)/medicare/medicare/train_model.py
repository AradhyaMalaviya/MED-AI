import pickle
import warnings

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder, StandardScaler

warnings.filterwarnings('ignore')

# 1. Load the dataset
df = pd.read_csv('Cleaned_Dataset.csv')

# 2. Map 'disease' to top 8 + 'Other'
top_diseases = ['Asthma', 'Bronchitis', 'Diabetes', 'Hypertension', 'Influenza', 'Migraine', 'Osteoporosis', 'Stroke']
df['disease_mapped'] = df['disease'].apply(lambda x: x if x in top_diseases else 'Other')

# 3. Features and Target
features = [
    'fever', 'cough', 'fatigue', 'difficulty_breathing', 'age', 'gender',
    'blood_pressure', 'cholesterol_level'
]
X = df[features]
y = df['disease_mapped']

# 4. Label Encode the target
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Save LabelEncoder
with open('disease_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)
print("Saved disease_encoder.pkl")
print("Classes:", le.classes_)

# 5. Build the Model Pipeline
numeric_features = ['age', 'blood_pressure', 'cholesterol_level']
categorical_features = ['fever', 'cough', 'fatigue', 'difficulty_breathing', 'gender']

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

model_pipeline = Pipeline(steps=[
    ('pre', preprocessor),
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
])

# 7. Train-Test Split & Train
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

print("Training model pipeline...")
model_pipeline.fit(X_train, y_train)

# Evaluate
train_acc = model_pipeline.score(X_train, y_train)
test_acc = model_pipeline.score(X_test, y_test)
print(f"Train Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")

# 8. Save the Pipeline
joblib.dump(model_pipeline, 'best_model.pkl')
print("Saved best_model.pkl")

print("Retraining completed successfully on current scikit-learn version:", sklearn.__version__)
