"""Loads the saved models and turns raw user input into a risk report."""
import os
import numpy as np
import pandas as pd
import joblib

from features import DISEASES, feature_names, label_of, to_frame

SAVED = os.path.join(os.path.dirname(__file__), "saved_models")
_cache = {}


def _load(disease):
    if disease not in _cache:
        path = os.path.join(SAVED, f"{disease}_model.joblib")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model for '{disease}' not found. Run: python ml/train.py")
        _cache[disease] = {
            "pipe": joblib.load(path),
            "background": pd.read_csv(os.path.join(SAVED, f"{disease}_background.csv")),
        }
    return _cache[disease]


def risk_level(p):
    return "Low" if p < 0.35 else "Moderate" if p < 0.65 else "High"


def explain(disease, pipe, background, row):
    """
    Per-feature contribution to this person's risk, in probability points.
    Positive = pushed risk up, negative = pulled it down. Uses SHAP; if SHAP fails for any
    reason, falls back to a simple 'replace with typical value' what-if so the API never breaks.
    """
    names = feature_names(disease)
    try:
        import shap
        f = lambda X: pipe.predict_proba(pd.DataFrame(X, columns=names))[:, 1]
        explainer = shap.Explainer(f, background[names])
        values = explainer(row[names]).values[0]
    except Exception:
        base = pipe.predict_proba(row[names])[0, 1]
        medians = background[names].median()
        values = []
        for n in names:
            alt = row[names].copy()
            alt[n] = medians[n]
            values.append(base - pipe.predict_proba(alt)[0, 1])
    return [(n, float(v)) for n, v in zip(names, values)]


def recommendations(disease, level, data):
    tips = []
    if disease == "diabetes":
        if data["Glucose"] >= 126: tips.append("Your glucose reading is high. Ask a doctor for a fasting blood sugar and HbA1c test.")
        elif data["Glucose"] >= 100: tips.append("Your glucose is slightly raised. Cut down on sugary drinks and refined carbs.")
        if data["BMI"] >= 25: tips.append("Losing even 5% of body weight can lower diabetes risk noticeably.")
        if data["BloodPressure"] >= 90: tips.append("Check your blood pressure regularly and reduce salt.")
    else:
        if data["chol"] >= 240: tips.append("Your cholesterol is high. Reduce fried and processed food and ask about a lipid profile.")
        if data["trestbps"] >= 140: tips.append("Your resting blood pressure is high. Monitor it and limit salt.")
        if data["exang"] == 1: tips.append("Chest pain during exercise should be checked by a cardiologist.")
        if data["thalach"] < 120: tips.append("A low peak heart rate in tests can signal poor fitness. Build up cardio gradually.")
    if level == "High":
        tips.insert(0, "Your risk is high. Please see a doctor soon for a proper check-up.")
    elif level == "Moderate":
        tips.insert(0, "Your risk is moderate. Book a routine check-up in the next few months.")
    else:
        tips.insert(0, "Your risk is low. Keep up healthy habits and get a yearly check-up.")
    tips.append("Aim for 150 minutes of moderate exercise a week and avoid smoking.")
    return tips


def predict(disease, data):
    """`data` must already be validated (see features.validate). Returns the JSON the frontend expects."""
    bundle = _load(disease)
    row = to_frame(disease, data)
    p = float(bundle["pipe"].predict_proba(row)[0, 1])

    contribs = explain(disease, bundle["pipe"], bundle["background"], row)
    contribs.sort(key=lambda x: abs(x[1]), reverse=True)
    top = [{"feature": label_of(disease, n), "impact": round(v, 3)} for n, v in contribs[:6]]

    level = risk_level(p)
    return {
        "risk_probability": round(p, 3),
        "risk_level": level,
        "prediction": int(p >= 0.5),
        "top_factors": top,
        "recommendations": recommendations(disease, level, data),
    }
