"""
Downloads the two public datasets into ml/data/.
  - Diabetes: Pima Indians Diabetes (768 rows), UCI / NIDDK
  - Heart:    Cleveland Heart Disease (303 rows), UCI
Run:  python ml/download_data.py
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

PIMA_URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
HEART_URL = "https://raw.githubusercontent.com/kb22/Heart-Disease-Prediction/master/dataset.csv"

# ---- Diabetes ----
cols = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin",
        "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"]
diabetes = pd.read_csv(PIMA_URL, header=None, names=cols)
diabetes.to_csv(os.path.join(DATA_DIR, "diabetes.csv"), index=False)
print("diabetes.csv:", diabetes.shape, "| positive rate:", round(diabetes["Outcome"].mean(), 2))

# ---- Heart ----
heart = pd.read_csv(HEART_URL, encoding="utf-8-sig")
# In this copy of the data, target = 1 means NO disease (checked: age, exang and oldpeak
# correlate negatively with it). We flip it so that 1 = disease, which is what a risk model needs.
heart["disease"] = 1 - heart["target"]
heart = heart.drop(columns=["target"])
heart.to_csv(os.path.join(DATA_DIR, "heart.csv"), index=False)
print("heart.csv:", heart.shape, "| positive rate:", round(heart["disease"].mean(), 2))
