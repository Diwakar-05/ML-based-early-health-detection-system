# EarlyCare AI - Backend + ML

## Setup
```bash
cd earlycare-backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

## 1. Download the datasets
```bash
python ml/download_data.py
```

## 2. Train the models
```bash
python ml/train.py
```
Prints a comparison table for every algorithm and saves the best model per disease in `ml/saved_models/`.

## 3. Run the API
```bash
python app.py
```
Open http://127.0.0.1:5000/api/health to check it works.
Then set `MOCK_MODE: false` in the frontend's `js/config.js`.

## Input fields the frontend must send
Diabetes: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
Heart: age, sex (0 female / 1 male), cp (0-3), trestbps, chol, fbs (0/1), restecg (0-2), thalach, exang (0/1), oldpeak, slope (0-2), ca (0-4), thal (0-3)

## Folder structure
```
app.py            Flask API
models.py         Database tables (users, predictions)
ml/features.py    Feature schema, ranges and validation
ml/download_data.py   Fetches the datasets
ml/train.py       Trains and compares the models
ml/predictor.py   Prediction, SHAP explanation, recommendations
ml/data/          CSV datasets
ml/saved_models/  Trained models and metrics
```
