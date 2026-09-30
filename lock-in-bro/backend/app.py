import math
import os
import re
from datetime import datetime, timezone
from collections import Counter, defaultdict
from flask import Flask, jsonify, render_template, request
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from models import db, FocusSession, BlockedAttempt


def create_app(config=None):
    app = Flask(__name__)
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///lock_in_bro.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config.update(SQLALCHEMY_DATABASE_URI=database_url,
                      SQLALCHEMY_TRACK_MODIFICATIONS=False, MAX_CONTENT_LENGTH=32768)
    if config:
        app.config.update(config)
    db.init_app(app)

    def body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ValueError('Send a JSON object.')
        return data

    def string(data, key, limit):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f'{key} must be nonempty text of at most {limit} characters.')
        return value.strip()

    def number(data, key, low, high, integer=False):
        value = data.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high or (integer and int(value) != value):
            raise ValueError(f'{key} must be {"a whole number" if integer else "a number"} between {low} and {high}.')
        return value

    def date(data, key):
        value = string(data, key, 64)
        try:
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                raise ValueError()
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            raise ValueError(f'{key} must be an ISO timestamp with a timezone.')

    def domain(value):
        if not isinstance(value, str) or len(value) > 253 or not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}', value):
            raise ValueError('Use a lowercase domain, without a URL or path.')
        return value

    @app.errorhandler(ValueError)
    def invalid(error):
        return jsonify(success=False, error=str(error)), 400

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        app.logger.error('Database operation failed: %s', type(error).__name__)
        return jsonify(success=False, error='Database unavailable. Please try again.'), 503

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(success=False, error=error.description), error.code

    @app.get('/api/health')
    def health():
        return jsonify(status='healthy')

    @app.post('/api/sessions')
    def start():
        data = body()
        client_id = string(data, 'client_id', 64)
        if not re.fullmatch(r'[A-Za-z0-9_-]+', client_id):
            raise ValueError('client_id may contain only letters, digits, underscores and hyphens.')
        domains = data.get('blocked_domains')
        if not isinstance(domains, list) or not 1 <= len(domains) <= 100:
            raise ValueError('blocked_domains must contain 1–100 domains.')
        session = FocusSession(client_id=client_id, task=string(data, 'task', 160),
            planned_minutes=number(data, 'planned_minutes', 1, 480, True),
            blocked_domains=list(dict.fromkeys(domain(d) for d in domains)),
            started_at=date(data, 'started_at'))
        db.session.add(session)
        db.session.commit()
        return jsonify(success=True, session_id=session.id), 201

    @app.post('/api/sessions/<int:session_id>/blocked')
    def blocked(session_id):
        session = db.get_or_404(FocusSession, session_id)
        data = body()
        name, timestamp = domain(data.get('domain')), date(data, 'timestamp')
        if name not in session.blocked_domains:
            raise ValueError('This domain is not in the session blocklist.')
        if timestamp < session.started_at or (session.ended_at and timestamp > session.ended_at):
            raise ValueError('Attempt timestamp is outside the session.')
        if session.ended_at:
            return jsonify(success=False, error='Session already finished.'), 409
        db.session.add(BlockedAttempt(session=session, domain=name, timestamp=timestamp))
        session.blocked_count = FocusSession.blocked_count + 1
        db.session.commit()
        return jsonify(success=True, blocked_count=session.blocked_count), 201

    @app.post('/api/sessions/<int:session_id>/finish')
    def finish(session_id):
        session = db.get_or_404(FocusSession, session_id)
        data = body()
        ended = date(data, 'ended_at')
        if ended < session.started_at:
            raise ValueError('ended_at cannot precede started_at.')
        if type(data.get('completed')) is not bool:
            raise ValueError('completed must be a boolean.')
        actual = number(data, 'actual_minutes', 0, 480)
        count = number(data, 'blocked_count', 0, 2147483647, True)
        score = None if data.get('focus_score') is None else number(data, 'focus_score', 0, 100)
        if session.ended_at:
            return jsonify(success=True, session_id=session.id)
        session.ended_at, session.completed = ended, data['completed']
        session.actual_minutes, session.focus_score = actual, score
        session.blocked_count = max(session.blocked_count, count)
        db.session.commit()
        return jsonify(success=True, session_id=session.id)

    @app.get('/api/stats/<client_id>')
    def stats(client_id):
        sessions = db.session.scalars(db.select(FocusSession).where(FocusSession.client_id == client_id).order_by(FocusSession.started_at.desc())).all()
        finished = [s for s in sessions if s.ended_at is not None]
        scores = [s.focus_score for s in finished if s.focus_score is not None]
        days = defaultdict(float)
        for s in finished:
            days[s.started_at.date().isoformat()] += s.actual_minutes or 0
        domains = Counter(a.domain for s in sessions for a in s.attempts)
        total = sum(s.actual_minutes or 0 for s in finished)
        def iso(value):
            return value.isoformat() + 'Z' if value else None
        return jsonify(total_focus_minutes=total, total_sessions=len(sessions),
            completed_sessions=sum(s.completed for s in finished),
            total_blocked_attempts=sum(s.blocked_count for s in sessions),
            average_focus_score=sum(scores)/len(scores) if scores else None,
            average_session_length=total/len(finished) if finished else 0,
            recent_sessions=[dict(id=s.id, task=s.task, planned_minutes=s.planned_minutes,
                actual_minutes=s.actual_minutes, blocked_count=s.blocked_count,
                focus_score=s.focus_score, completed=s.completed,
                started_at=iso(s.started_at), ended_at=iso(s.ended_at)) for s in sessions[:20]],
            most_blocked_domains=[dict(domain=d, count=n) for d, n in domains.most_common()],
            focus_by_day=[dict(day=d, minutes=m) for d, m in sorted(days.items())])

    @app.get('/')
    def dashboard():
        return render_template('dashboard.html')

    @app.cli.command('init-db')
    def init_db():
        """Create tables and add Phase 2 columns to a local Phase 1 SQLite DB."""
        db.create_all()
        if db.engine.dialect.name == 'sqlite':
            columns = {c['name'] for c in inspect(db.engine).get_columns('focus_session')}
            for name, ddl in [('actual_minutes', 'FLOAT'), ('focus_score', 'FLOAT'),
                              ('blocked_domains', "JSON NOT NULL DEFAULT '[]'")]:
                if name not in columns:
                    db.session.execute(text(f'ALTER TABLE focus_session ADD COLUMN {name} {ddl}'))
            db.session.commit()
        print('Database initialized.')

    return app


app = create_app()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
