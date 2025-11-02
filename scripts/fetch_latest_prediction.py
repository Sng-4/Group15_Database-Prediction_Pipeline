#!/usr/bin/env python3
"""Fetch the most recent ECG test via the FastAPI service and run a heart-disease prediction."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import requests

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

DEFAULT_BASE_URL = os.environ.get("HEART_API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent / "models" / "heart_disease_model.joblib"
)


def fetch_json(url: str, *, timeout: int = 10) -> Dict[str, Any]:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError(f"Unexpected response type from {url!r}: {type(payload).__name__}")
    return payload


def fetch_latest_test(base_url: str) -> Dict[str, Any]:
    base_url = base_url.rstrip("/")
    return fetch_json(f"{base_url}/ecg_tests/latest")


def fetch_encounter(base_url: str, encounter_id: int) -> Optional[Dict[str, Any]]:
    try:
        return fetch_json(f"{base_url.rstrip('/')}/encounters/{encounter_id}")
    except requests.HTTPError as exc:  # pragma: no cover - informational only
        if exc.response is not None and exc.response.status_code == 404:
            return None
        raise


def fetch_patient(base_url: str, patient_id: int) -> Optional[Dict[str, Any]]:
    try:
        return fetch_json(f"{base_url.rstrip('/')}/patients/{patient_id}")
    except requests.HTTPError as exc:  # pragma: no cover - informational only
        if exc.response is not None and exc.response.status_code == 404:
            return None
        raise


def load_model(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Could not find model at {model_path}. Run the training script or place your trained model there."
        )
    artifact = joblib.load(model_path)
    if isinstance(artifact, dict) and "model" in artifact:
        model = artifact["model"]
        feature_keys = artifact.get("feature_keys")
        if feature_keys and list(feature_keys) != FEATURE_KEYS:
            raise ValueError(
                "Model feature order does not match expected keys. "
                f"Expected {FEATURE_KEYS}, got {feature_keys}."
            )
        return model
    return artifact


def prepare_features(test_record: Dict[str, Any]) -> np.ndarray:
    missing = [key for key in FEATURE_KEYS if test_record.get(key) is None]
    if missing:
        raise ValueError(
            f"Latest ECG test is missing required feature(s): {', '.join(missing)}"
        )

    feature_row = []
    for key in FEATURE_KEYS:
        value = test_record[key]
        try:
            feature_row.append(float(value))
        except (TypeError, ValueError):
            raise ValueError(f"Feature {key!r} value {value!r} is not numeric") from None

    return np.asarray(feature_row, dtype=float).reshape(1, -1)


def format_context(latest_test: Dict[str, Any], encounter: Optional[Dict[str, Any]], patient: Optional[Dict[str, Any]]) -> str:
    context = {
        "test": {k: latest_test.get(k) for k in ("test_id", "encounter_id", "target", *FEATURE_KEYS)},
        "encounter": encounter,
        "patient": patient,
    }
    return json.dumps(context, default=str, indent=2)


def load_json_fixture(json_path: Path) -> Dict[str, Any]:
    with json_path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, dict):
        raise ValueError("JSON input must be an object with ECG feature keys")
    return data


def run(base_url: str, model_path: Path, input_json: Optional[Path] = None) -> int:
    if input_json is not None:
        print(f"Loading ECG test from JSON file {input_json} ...")
        latest_test = load_json_fixture(input_json)
        encounter = None
        patient = None
    else:
        print(f"Fetching latest ECG test from {base_url} ...")
        latest_test = fetch_latest_test(base_url)

        encounter = fetch_encounter(base_url, latest_test.get("encounter_id"))
        patient = None
        if encounter is not None:
            patient_id = encounter.get("patient_id")
            if patient_id is not None:
                patient = fetch_patient(base_url, int(patient_id))

    if "target" in latest_test:
        print("Note: 'target' field was returned by the API and will be ignored for prediction.")

    model = load_model(model_path)
    features = prepare_features(latest_test)

    prediction = model.predict(features)[0]
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        positive_prob = float(probabilities[1])
    else:
        positive_prob = float(prediction)

    print("Context for prediction:")
    print(format_context(latest_test, encounter, patient))

    print("\nPrediction results:")
    print(f"Predicted class: {int(prediction)}")
    print(f"Probability of heart disease (class 1): {positive_prob:.4f}")

    if latest_test.get("target") is not None:
        print(f"Ground truth target from record: {latest_test['target']}")

    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL of the FastAPI heart disease service (default: %(default)s)",
    )
    parser.add_argument(
        "--model-path",
        default=str(DEFAULT_MODEL_PATH),
        help="Path to the serialized sklearn model (default: %(default)s)",
    )
    parser.add_argument(
        "--input-json",
        help="Optional path to a JSON file containing ECG test data (bypasses API fetch)",
    )

    args = parser.parse_args(argv)
    input_json = Path(args.input_json).resolve() if args.input_json else None
    try:
        return run(args.base_url, Path(args.model_path), input_json)
    except requests.HTTPError as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        print(f"HTTP error while talking to API: {message}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
