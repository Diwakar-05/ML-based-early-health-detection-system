"""
Trains and compares several algorithms for each disease, then saves the best one.
Run:  python ml/train.py            (both diseases)
      python ml/train.py diabetes   (one disease)

Outputs (in ml/saved_models/):
  <disease>_model.joblib       best pipeline (imputer + scaler + classifier)
  <disease>_background.csv     small sample of training rows used by SHAP
  <disease>_metrics.json       scores of every model (shown on the About page)
"""
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from features import DISEASES, feature_names, mark_missing

try:
    from xgboost import XGBClassifier
except ImportError:  # XGBoost is optional
    XGBClassifier = None

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "data")
OUT_DIR = os.path.join(HERE, "saved_models")
os.makedirs(OUT_DIR, exist_ok=True)
SEED = 42


def build_models():
    """Candidate algorithms. Each is wrapped in a pipeline so preprocessing is learned on training data only."""
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random Forest": GridSearchCV(
            RandomForestClassifier(class_weight="balanced", random_state=SEED),
            {"n_estimators": [200, 400], "max_depth": [4, 6, None], "min_samples_leaf": [1, 3]},
            scoring="roc_auc", cv=3, n_jobs=-1),
        "SVM": SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=SEED),
    }
    if XGBClassifier is not None:
        models["XGBoost"] = XGBClassifier(
            n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.9,
            eval_metric="logloss", random_state=SEED)
    return models


def make_pipeline(clf):
    return Pipeline([("imputer", SimpleImputer(strategy="median")),
                     ("scaler", StandardScaler()),
                     ("clf", clf)])


def train_disease(disease):
    cfg = DISEASES[disease]
    df = pd.read_csv(os.path.join(DATA_DIR, f"{disease}.csv"))
    X = mark_missing(df[feature_names(disease)].astype(float), cfg)
    y = df[cfg["target"]]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED)
    print(f"\n=== {disease.upper()} | train {len(X_train)} / test {len(X_test)} | positive rate {y.mean():.2f}")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    results, fitted = [], {}

    for name, clf in build_models().items():
        pipe = make_pipeline(clf)
        cv_auc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc").mean()
        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
        row = {
            "model": name,
            "accuracy": round(accuracy_score(y_test, pred), 4),
            "precision": round(precision_score(y_test, pred), 4),
            "recall": round(recall_score(y_test, pred), 4),   # most important for screening
            "f1": round(f1_score(y_test, pred), 4),
            "roc_auc": round(roc_auc_score(y_test, proba), 4),
            "cv_roc_auc": round(cv_auc, 4),
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        }
        results.append(row)
        fitted[name] = pipe
        print(f"{name:20s} acc={row['accuracy']:.3f} prec={row['precision']:.3f} "
              f"rec={row['recall']:.3f} f1={row['f1']:.3f} auc={row['roc_auc']:.3f} cv_auc={row['cv_roc_auc']:.3f}")

    # Pick the winner by cross-validated ROC-AUC (more stable than a single test split).
    best = max(results, key=lambda r: r["cv_roc_auc"])["model"]
    print(f"--> Best model: {best}")

    joblib.dump(fitted[best], os.path.join(OUT_DIR, f"{disease}_model.joblib"))
    X_train.sample(min(60, len(X_train)), random_state=SEED).to_csv(
        os.path.join(OUT_DIR, f"{disease}_background.csv"), index=False)
    with open(os.path.join(OUT_DIR, f"{disease}_metrics.json"), "w") as f:
        json.dump({"disease": disease, "best_model": best, "train_size": len(X_train),
                   "test_size": len(X_test), "models": results}, f, indent=2)


if __name__ == "__main__":
    targets = sys.argv[1:] or list(DISEASES.keys())
    for d in targets:
        train_disease(d)
    print("\nDone. Models saved in ml/saved_models/")
