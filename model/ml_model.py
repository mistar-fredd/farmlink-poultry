"""
FARMLINK POULTRY - Machine Learning Module
Generates a synthetic dataset of bird health metrics, trains a
Random Forest classifier to predict health status ("Healthy" or "At Risk"),
and saves the trained model to disk for use by the Flask application.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib


def generate_dataset(n_samples=500):
    """Generate a synthetic bird health dataset."""
    np.random.seed(42)

    # Features
    age_weeks = np.random.randint(1, 104, size=n_samples)
    weight_kg = np.round(np.random.uniform(0.5, 5.0, size=n_samples), 2)
    previous_health_issues = np.random.randint(0, 6, size=n_samples)
    flock_mortality_rate = np.round(np.random.uniform(0.0, 0.3, size=n_samples), 3)
    vaccination_status = np.random.choice([0, 1], size=n_samples, p=[0.2, 0.8])

    # Target: "At Risk" if multiple risk factors are present
    risk_score = (
        (age_weeks > 78).astype(int)
        + (previous_health_issues >= 3).astype(int)
        + (flock_mortality_rate > 0.15).astype(int)
        + (vaccination_status == 0).astype(int)
        + (weight_kg < 1.2).astype(int)
    )
    # Add some noise
    noise = np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15])
    risk_score = risk_score + noise

    status = np.where(risk_score >= 2, "At Risk", "Healthy")

    df = pd.DataFrame({
        "age_weeks": age_weeks,
        "weight_kg": weight_kg,
        "previous_health_issues": previous_health_issues,
        "flock_mortality_rate": flock_mortality_rate,
        "vaccination_status": vaccination_status,
        "status": status,
    })

    return df


def train_model():
    """Train the Random Forest model and save it."""
    print("=" * 50)
    print("FARMLINK POULTRY - ML Model Training")
    print("=" * 50)

    # Generate data
    print("\n[1/4] Generating synthetic dataset...")
    df = generate_dataset(n_samples=500)
    print(f"      Dataset shape: {df.shape}")
    print(f"      Class distribution:\n{df['status'].value_counts().to_string()}")

    # Prepare features and target
    print("\n[2/4] Preparing features...")
    feature_columns = [
        "age_weeks",
        "weight_kg",
        "previous_health_issues",
        "flock_mortality_rate",
        "vaccination_status",
    ]
    X = df[feature_columns]
    y = df["status"]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    print("\n[3/4] Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\n      Classification Report:")
    print(classification_report(y_test, y_pred))

    # Save model
    print("[4/4] Saving model...")
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, "bird_health_model.pkl")
    joblib.dump(model, model_path)
    print(f"      Model saved to: {model_path}")

    # Save feature column names alongside the model
    columns_path = os.path.join(model_dir, "feature_columns.pkl")
    joblib.dump(feature_columns, columns_path)
    print(f"      Feature columns saved to: {columns_path}")

    print("\n" + "=" * 50)
    print("Training complete!")
    print("=" * 50)

    return model


if __name__ == "__main__":
    train_model()
