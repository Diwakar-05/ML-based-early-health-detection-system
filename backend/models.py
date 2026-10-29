"""Database tables (SQLite via SQLAlchemy)."""
import json
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    predictions = db.relationship("Prediction", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    disease = db.Column(db.String(20), nullable=False)
    risk_probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(10), nullable=False)
    inputs = db.Column(db.Text, nullable=False)           # JSON string
    top_factors = db.Column(db.Text, nullable=False)      # JSON string
    recommendations = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id, "disease": self.disease,
            "risk_probability": self.risk_probability, "risk_level": self.risk_level,
            "inputs": json.loads(self.inputs), "top_factors": json.loads(self.top_factors),
            "recommendations": json.loads(self.recommendations),
            "created_at": self.created_at.isoformat(),
        }
