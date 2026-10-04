from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_sub = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

class ClientInstallation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

class FocusSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(64), nullable=False)
    task = db.Column(db.String(160), nullable=False)
    planned_minutes = db.Column(db.Integer, nullable=False)
    actual_minutes = db.Column(db.Float)
    focus_score = db.Column(db.Float)
    blocked_domains = db.Column(db.JSON, nullable=False, default=list)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    ended_at = db.Column(db.DateTime(timezone=True))
    completed = db.Column(db.Boolean, nullable=False, default=False)
    blocked_count = db.Column(db.Integer, nullable=False, default=0)
    attempts = db.relationship("BlockedAttempt", back_populates="session", cascade="all, delete-orphan")

class BlockedAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("focus_session.id"), nullable=False)
    domain = db.Column(db.String(253), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    session = db.relationship("FocusSession", back_populates="attempts")
