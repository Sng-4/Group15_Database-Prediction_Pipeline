#!/usr/bin/env python3
"""Train a simple logistic regression model for heart disease prediction and persist it to disk."""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_KEYS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "heart_disease_model.joblib"


def generate_synthetic_dataset(n_samples: int = 1200, random_state: int = 2024):
    rng = np.random.default_rng(random_state)

    age = rng.integers(29, 78, size=n_samples)
    sex = rng.integers(0, 2, size=n_samples)
    cp = rng.integers(0, 4, size=n_samples)
    trestbps = rng.normal(130, 17, size=n_samples).clip(90, 200)
    chol = rng.normal(245, 52, size=n_samples).clip(150, 400)
    fbs = rng.integers(0, 2, size=n_samples)
    restecg = rng.integers(0, 3, size=n_samples)
    thalach = rng.normal(149, 23, size=n_samples).clip(70, 210)
    exang = rng.integers(0, 2, size=n_samples)
    oldpeak = rng.normal(1.0, 1.1, size=n_samples).clip(0, 6)
    slope = rng.integers(0, 3, size=n_samples)
    ca = rng.integers(0, 5, size=n_samples)
    thal = rng.integers(0, 4, size=n_samples)

    # Logistic generating function with handcrafted weights for interpretability.
    logits = (
        -4.5
        + 0.035 * (age - 54)
        + 0.9 * (cp == 2)
        + 1.2 * (cp == 3)
        + 0.015 * (trestbps - 120)
        + 0.012 * (chol - 200)
        + 0.8 * (fbs == 1)
        + 0.25 * (restecg == 2)
        - 0.03 * (thalach - 150)
        + 0.9 * exang
        + 0.7 * oldpeak
        + 0.4 * (slope == 2)
        + 0.5 * (ca >= 2)
        + 0.6 * (thal >= 2)
    )

    probabilities = 1 / (1 + np.exp(-logits))
    target = rng.binomial(1, probabilities)

    data = np.column_stack(
        [
            age,
            sex,
            cp,
            trestbps,
            chol,
            fbs,
            restecg,
            thalach,
            exang,
            oldpeak,
            slope,
            ca,
            thal,
        ]
    )
    return data.astype(float), target.astype(int)


def build_model(random_state: int = 42) -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "log_reg",
                LogisticRegression(max_iter=200, solver="lbfgs", random_state=random_state),
            ),
        ]
    )


def train_and_save_model(output_path: Path = DEFAULT_OUTPUT) -> Path:
    X, y = generate_synthetic_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=123, stratify=y
    )

    model = build_model()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "feature_keys": FEATURE_KEYS, "score": score}, output_path)
    return output_path


def main() -> None:
    output_path = train_and_save_model()
    print(f"Model saved to {output_path}")


if __name__ == "__main__":
    main()
