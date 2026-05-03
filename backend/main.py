import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# ── Load bundle (no function inside, safe to unpickle) ───────────────────────
bundle        = joblib.load("kdd_pipeline.joblib")
pipeline      = bundle["pipeline"]
encoders      = bundle["encoders"]
metadata      = bundle["metadata"]
skew_col_idx  = bundle["skew_col_idx"]

le_service    = encoders["le_service"]
le_protocol   = encoders["le_protocol"]
le_flag       = encoders["le_flag"]
FEATURE_NAMES = metadata["feature_names"]
DROPPED_COLS  = metadata["dropped_cols"]

app = FastAPI(title="KDD Intrusion Detection API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NetworkRecord(BaseModel):
    model_config = {"extra": "allow"}


def apply_log1p(X: np.ndarray) -> np.ndarray:
    """Apply log1p only to the skewed columns — mirrors Colab's log1p_transform."""
    X = np.array(X, dtype=float)
    X[:, skew_col_idx] = np.log1p(np.clip(X[:, skew_col_idx], 0, None))
    return X


def preprocess(record: dict) -> np.ndarray:
    df = pd.DataFrame([record])

    # 1. Drop zero-variance columns
    df.drop(columns=[c for c in DROPPED_COLS if c in df.columns], inplace=True)

    # 2. Encode categoricals
    df["service"]       = le_service.transform(df["service"])
    df["protocol_type"] = le_protocol.transform(df["protocol_type"])
    df["flag"]          = le_flag.transform(df["flag"])

    # 3. Enforce correct column order
    df = df[FEATURE_NAMES]

    # 4. Apply log1p manually (replaces FunctionTransformer step)
    X = apply_log1p(df.values)

    return X


@app.post("/api/predict")
def predict(record: NetworkRecord):
    X = preprocess(record.model_dump())
    prediction  = pipeline.predict(X)[0]
    probability = pipeline.predict_proba(X)[0]
    label       = metadata["classes"][int(prediction)]

    return {
        "prediction":  label,
        "is_attack":   bool(prediction),
        "confidence":  round(float(max(probability)), 4),
        "probabilities": {
            "Normal": round(float(probability[0]), 4),
            "Attack": round(float(probability[1]), 4),
        }
    }


@app.get("/api/model-info")
def model_info():
    return metadata