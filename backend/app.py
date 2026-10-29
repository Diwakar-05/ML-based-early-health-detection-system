"""
EarlyCare AI - Flask REST API.
Run:  python app.py        (serves on http://127.0.0.1:5000)

Endpoints
  POST   /api/auth/register          {name, email, password}      -> {token, user}
  POST   /api/auth/login             {email, password}            -> {token, user}
  POST   /api/predict/<disease>      disease = diabetes | heart   -> risk report (saved to history if logged in)
  GET    /api/history                (JWT required)               -> list of past predictions
  DELETE /api/history/<id>           (JWT required)
  GET    /api/model-metrics                                       -> scores of all trained models
"""
import json
import os
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (JWTManager, create_access_token, get_jwt_identity,
                                jwt_required, verify_jwt_in_request)

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "ml"))

from features import DISEASES, validate   # noqa: E402
import predictor                          # noqa: E402
from models import Prediction, User, db   # noqa: E402

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE, "earlycare.db")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "change-this-secret-in-production-0123456789")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 24  # 1 day
CORS(app)  # allow the frontend (a different origin) to call the API
db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()


def error(message, status=400):
    return jsonify({"message": message}), status


@jwt.unauthorized_loader
@jwt.invalid_token_loader
def _unauth(reason):
    return error("Please log in to continue.", 401)


@jwt.expired_token_loader
def _expired(h, p):
    return error("Session expired. Please log in again.", 401)


# ---------------- Auth ----------------
@app.post("/api/auth/register")
def register():
    body = request.get_json(silent=True) or {}
    name, email, password = (body.get("name") or "").strip(), (body.get("email") or "").strip().lower(), body.get("password") or ""
    if len(name) < 2 or "@" not in email or len(password) < 8:
        return error("Enter a name, a valid email and a password of at least 8 characters.")
    if User.query.filter_by(email=email).first():
        return error("An account with this email already exists.", 409)
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"token": create_access_token(identity=str(user.id)), "user": user.to_dict()}), 201


@app.post("/api/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=(body.get("email") or "").strip().lower()).first()
    if not user or not user.check_password(body.get("password") or ""):
        return error("Incorrect email or password.", 401)
    return jsonify({"token": create_access_token(identity=str(user.id)), "user": user.to_dict()})


# ---------------- Prediction ----------------
@app.post("/api/predict/<disease>")
def predict(disease):
    if disease not in DISEASES:
        return error("Unknown disease. Use 'diabetes' or 'heart'.", 404)
    data, problem = validate(disease, request.get_json(silent=True) or {})
    if problem:
        return error(problem)
    try:
        result = predictor.predict(disease, data)
    except FileNotFoundError as e:
        return error(str(e), 503)

    # Save to history only when the caller is logged in (the token is optional here).
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
    except Exception:
        uid = None
    if uid:
        row = Prediction(user_id=int(uid), disease=disease,
                         risk_probability=result["risk_probability"], risk_level=result["risk_level"],
                         inputs=json.dumps(data), top_factors=json.dumps(result["top_factors"]),
                         recommendations=json.dumps(result["recommendations"]))
        db.session.add(row)
        db.session.commit()
        result["id"] = row.id
    return jsonify(result)


# ---------------- History ----------------
@app.get("/api/history")
@jwt_required()
def history():
    rows = Prediction.query.filter_by(user_id=int(get_jwt_identity())).order_by(Prediction.created_at.desc()).all()
    return jsonify([r.to_dict() for r in rows])


@app.delete("/api/history/<int:pid>")
@jwt_required()
def delete_history(pid):
    row = Prediction.query.filter_by(id=pid, user_id=int(get_jwt_identity())).first()
    if not row:
        return error("Record not found.", 404)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "Deleted."})


# ---------------- Model metrics (About page) ----------------
@app.get("/api/model-metrics")
def model_metrics():
    out = {}
    for d in DISEASES:
        path = os.path.join(BASE, "ml", "saved_models", f"{d}_metrics.json")
        if os.path.exists(path):
            with open(path) as f:
                out[d] = json.load(f)
    return jsonify(out)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
