# Heart Disease Data Pipeline

This repository contains a small data pipeline that spans a MySQL-backed FastAPI service, a MongoDB bootstrapper, and a lightweight machine-learning workflow for heart disease prediction.

## Components

### FastAPI (MySQL) service
- Location: `heart_api/main.py`
- Responsibilities: CRUD for patients, encounters, and ECG tests plus audit logging via MySQL stored procedures and triggers.
- Requirements: Python 3.10+, a running MySQL instance seeded with `mySQl/heart_schema.sql`.
- Run locally:
  ```bash
  cd heart_api
  python3 -m venv .venv
  source .venv/bin/activate
  pip install fastapi uvicorn mysql-connector-python
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```

### MongoDB bootstrapper
- Location: `mongoDb/`
- Responsibilities: create collections, indexes, and seed documents in MongoDB.
- Run locally:
  ```bash
  cd mongoDb/mongodb-setup
  npm install
  npm run setup
  npm run dev
  ```

### Machine-learning workflow
- Training script: `models/train_sample_model.py`
  - Generates a synthetic dataset, trains a logistic regression pipeline, and saves the artifact to `models/heart_disease_model.joblib`.
  - Install dependencies and train:
    ```bash
    python3 -m pip install --user numpy scikit-learn joblib
    python3 models/train_sample_model.py
    ```
- Prediction script: `scripts/fetch_latest_prediction.py`
  - Fetches the most recent ECG record from the FastAPI service (or from a JSON fixture) and runs a prediction with the saved model.
  - Usage:
    ```bash
    # Fetch live data from FastAPI
    python3 scripts/fetch_latest_prediction.py --base-url http://127.0.0.1:8000

    # Offline mode using a JSON fixture
    python3 scripts/fetch_latest_prediction.py --input-json scripts/sample_ecg_input.json
    ```
  - Environment variables:
    - `HEART_API_BASE_URL`: optional override for the API base URL.

