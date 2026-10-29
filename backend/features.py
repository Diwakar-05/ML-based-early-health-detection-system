"""
Single source of truth for the feature schema of each disease.
Used by training (train.py), prediction (predictor.py) and API validation (app.py),
so the model always sees the same columns in the same order.
"""
import numpy as np
import pandas as pd

# feature: (min, max, label shown to the user)
DISEASES = {
    "diabetes": {
        "target": "Outcome",
        "features": {
            "Pregnancies":             (0, 20,    "Pregnancies"),
            "Glucose":                 (40, 400,  "Glucose"),
            "BloodPressure":           (30, 200,  "Blood pressure"),
            "SkinThickness":           (0, 100,   "Skin thickness"),
            "Insulin":                 (0, 900,   "Insulin"),
            "BMI":                     (10, 70,   "BMI"),
            "DiabetesPedigreeFunction": (0.05, 2.5, "Family history score"),
            "Age":                     (1, 120,   "Age"),
        },
        # In the Pima dataset a 0 here means "not measured", so it is treated as missing.
        "zero_is_missing": ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"],
    },
    "heart": {
        "target": "disease",
        "features": {
            "age":      (1, 120,  "Age"),
            "sex":      (0, 1,    "Sex"),
            "cp":       (0, 3,    "Chest pain type"),
            "trestbps": (70, 250, "Resting blood pressure"),
            "chol":     (100, 600, "Cholesterol"),
            "fbs":      (0, 1,    "Fasting blood sugar > 120"),
            "restecg":  (0, 2,    "Resting ECG"),
            "thalach":  (60, 220, "Max heart rate"),
            "exang":    (0, 1,    "Exercise-induced angina"),
            "oldpeak":  (0, 7,    "ST depression"),
            "slope":    (0, 2,    "ST slope"),
            "ca":       (0, 4,    "Major vessels coloured"),
            "thal":     (0, 3,    "Thalassemia"),
        },
        "zero_is_missing": [],
    },
}


def feature_names(disease):
    return list(DISEASES[disease]["features"].keys())


def label_of(disease, feature):
    return DISEASES[disease]["features"][feature][2]


def validate(disease, data):
    """Return (clean_dict, error_message). error_message is None when the input is valid."""
    clean = {}
    for name, (lo, hi, label) in DISEASES[disease]["features"].items():
        if name not in data or data[name] in ("", None):
            return None, f"{label} is required."
        try:
            value = float(data[name])
        except (TypeError, ValueError):
            return None, f"{label} must be a number."
        if not (lo <= value <= hi):
            return None, f"{label} must be between {lo} and {hi}."
        clean[name] = value
    return clean, None


def to_frame(disease, data):
    """One-row DataFrame in training column order, with 'zero = missing' columns set to NaN."""
    cfg = DISEASES[disease]
    df = pd.DataFrame([data], columns=feature_names(disease)).astype(float)
    return mark_missing(df, cfg)


def mark_missing(df, cfg):
    for col in cfg["zero_is_missing"]:
        df[col] = df[col].replace(0, np.nan)
    return df
