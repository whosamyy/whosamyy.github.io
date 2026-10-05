from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

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

class PigProfile(db.Model):
    """Only cosmetic choices are stored; rewards remain derived from focus rows."""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    coins_spent = db.Column(db.Integer, nullable=False, default=0)
    purchased_items = db.Column(db.JSON, nullable=False, default=list)
    equipped_items = db.Column(db.JSON, nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    __table_args__ = (db.CheckConstraint('coins_spent >= 0', name='pig_nonnegative_spend'),)

    @validates('purchased_items', 'equipped_items')
    def validate_items(self, key, value):
        from pig_room import ITEM_BY_ID
        if value is None and key == 'equipped_items':
            return None
        if not isinstance(value, list) or any(not isinstance(item, str) or item not in ITEM_BY_ID for item in value):
            raise ValueError('Room items must be a list of known catalog IDs.')
        if key == 'purchased_items' and any(ITEM_BY_ID[item]['category'] == 'accessory' for item in value):
            raise ValueError('Accessories unlock through XP, not coin purchases.')
        return sorted(set(value))
