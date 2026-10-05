import math
import os
import re
import secrets
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
from flask import Flask, abort, jsonify, redirect, render_template, request, session as login_session, url_for
from flask_session import Session
from cachelib.file import FileSystemCache
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException, SecurityError
from models import db, FocusSession, BlockedAttempt, ClientInstallation, PigProfile, User
from auth import init_auth, current_user, claim_client, valid_client_id, auth_configured
from pig_room import ITEM_BY_ID, room_state


def as_utc(value):
    # SQLite returns naive UTC values; PostgreSQL returns timezone-aware values.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def create_app(config=None):
    app = Flask(__name__)
    on_render = os.environ.get('RENDER') == 'true'
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///lock_in_bro.db')
    # Select psycopg 3 explicitly; preserve credentials and query parameters verbatim.
    for prefix in ('postgres://', 'postgresql://'):
        if database_url.startswith(prefix):
            database_url = 'postgresql+psycopg://' + database_url[len(prefix):]
            break
    app.config.update(SQLALCHEMY_DATABASE_URI=database_url,
                      SQLALCHEMY_TRACK_MODIFICATIONS=False, MAX_CONTENT_LENGTH=32768,
                      SECRET_KEY=os.environ.get('SECRET_KEY'),
                      GOOGLE_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID'),
                      GOOGLE_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET'),
                      SESSION_TYPE='cachelib', SESSION_USE_SIGNER=True,
                      SESSION_PERMANENT=False, SESSION_COOKIE_NAME='lock_dashboard',
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                      SESSION_COOKIE_SECURE=on_render,
                      PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
                      SESSION_REFRESH_EACH_REQUEST=False,
                      TRUSTED_HOSTS=['lock-in-bro.onrender.com'] if on_render else ['127.0.0.1', 'localhost'],
                      OAUTH_REDIRECT_URI=('https://lock-in-bro.onrender.com/auth/callback' if on_render
                                          else 'http://127.0.0.1:5000/auth/callback'))
    if config:
        app.config.update(config)
    db.init_app(app)
    if 'SESSION_CACHELIB' not in app.config:
        # All Gunicorn workers on one Render instance share this transient store.
        # No OAuth tokens are saved; restarts may sign users out, never lose analytics.
        cache_dir = os.path.join(app.instance_path, 'dashboard_sessions')
        os.makedirs(cache_dir, mode=0o700, exist_ok=True)
        app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir=cache_dir, threshold=10000)
    if app.config.get('SECRET_KEY'):
        Session(app)
    if on_render:
        # Render terminates TLS. Trust only its single forwarded scheme hop,
        # not a forwarded host; callback URLs are fixed above.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=0, x_proto=1, x_host=0, x_port=0, x_prefix=0)
    init_auth(app)

    @app.after_request
    def protect_read_responses(response):
        if request.endpoint not in ('static', 'health'):
            response.headers['Cache-Control'] = 'no-store'
            response.headers['Referrer-Policy'] = 'no-referrer'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
        return response

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
            return parsed.astimezone(timezone.utc)
        except ValueError:
            raise ValueError(f'{key} must be an ISO timestamp with a timezone.')

    def domain(value):
        if not isinstance(value, str) or len(value) > 253 or not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}', value):
            raise ValueError('Use a lowercase domain, without a URL or path.')
        return value

    @app.errorhandler(ValueError)
    def invalid(error):
        db.session.rollback()
        return jsonify(success=False, error=str(error)), 400

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        app.logger.error('Database operation failed: %s', type(error).__name__)
        message = 'Database unavailable. Please try again.'
        if request.path.startswith('/api/'):
            return jsonify(success=False, error=message), 503
        return render_template('auth_error.html', message=message), 503

    @app.errorhandler(HTTPException)
    def http_error(error):
        if isinstance(error, SecurityError):
            # An untrusted host has no URL adapter for rendering templates.
            return 'Invalid request host.', 400
        if request.path.startswith('/api/'):
            return jsonify(success=False, error=error.description), error.code
        return render_template('auth_error.html', message=error.description), error.code

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
        # A retry (including recovery of a locally saved recap) must reuse the
        # original row rather than count the same session twice.
        existing = db.session.scalar(db.select(FocusSession).where(
            FocusSession.client_id == client_id,
            FocusSession.started_at == session.started_at))
        if existing:
            return jsonify(success=True, session_id=existing.id), 200
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
        if timestamp < as_utc(session.started_at) or (session.ended_at and timestamp > as_utc(session.ended_at)):
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
        if ended < as_utc(session.started_at):
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
        user = current_user()
        if user is None:
            abort(401, description='Sign in to view your focus history.')
        if not valid_client_id(client_id):
            abort(400, description='Invalid installation ID.')
        owned = db.session.scalar(db.select(ClientInstallation).where(
            ClientInstallation.client_id == client_id, ClientInstallation.user_id == user.id))
        if owned is None:
            abort(403, description='This history is not available to your account.')
        return stats_for_clients([client_id])

    def owned_pig_sessions(user):
        clients = db.select(ClientInstallation.client_id).where(ClientInstallation.user_id == user.id)
        return db.session.scalars(db.select(FocusSession).where(FocusSession.client_id.in_(clients))).all()

    def pig_user(write=False):
        user = current_user()
        if user is None:
            abort(401, description='Sign in to customize your pig room.')
        if write:
            expected = login_session.get('csrf_token')
            supplied = request.headers.get('X-CSRF-Token', '')
            if not isinstance(expected, str) or not supplied or not secrets.compare_digest(expected.encode('utf-8'), supplied.encode('utf-8')):
                abort(403, description='Please reload your dashboard before customizing.')
            # Serialize purchases/equipment for this account before reading its profile.
            # A row update locks on PostgreSQL and acquires SQLite's write lock.
            db.session.execute(db.update(User).where(User.id == user.id).values(id=User.id))
        return user

    def current_pig_state(user, unlocked=False):
        return room_state(owned_pig_sessions(user), db.session.get(PigProfile, user.id),
                          zone=request.args.get('timezone'), unlocked_something=unlocked)

    @app.get('/api/me/pig')
    def my_pig():
        return jsonify(pig=current_pig_state(pig_user()))

    @app.post('/api/me/pig/unlock')
    @app.post('/api/me/pig/equip')
    def customize_pig():
        user = pig_user(write=True)
        data = body()
        if set(data) - {'item_id', 'equipped'}:
            raise ValueError('Only item_id and equipped are accepted; ownership comes from sign-in.')
        item_id = data.get('item_id')
        if not isinstance(item_id, str) or item_id not in ITEM_BY_ID:
            raise ValueError('Choose an item from the pig room catalog.')
        state = current_pig_state(user)
        item = next(i for i in state['items'] if i['id'] == item_id)
        profile = db.session.get(PigProfile, user.id)
        if profile is None:
            profile = PigProfile(user_id=user.id, coins_spent=0, purchased_items=[],
                                 equipped_items=state['equipped_items'])
            db.session.add(profile)
        unlocked = False
        if request.path.endswith('/unlock'):
            if not item['unlocked']:
                if item['category'] == 'accessory':
                    raise ValueError('This accessory unlocks through XP levels.')
                if state['coins'] < item['cost']:
                    raise ValueError('A few more focused minutes will unlock this item.')
                profile.purchased_items = list(profile.purchased_items) + [item_id]
                profile.coins_spent += item['cost']
                unlocked = True
        else:
            if type(data.get('equipped')) is not bool:
                raise ValueError('equipped must be a boolean.')
            if not item['unlocked']:
                raise ValueError('Unlock this item before equipping it.')
            equipped = set(profile.equipped_items or [])
            if data['equipped']:
                equipped.add(item_id)
            else:
                equipped.discard(item_id)
            profile.equipped_items = sorted(equipped)
        db.session.commit()
        return jsonify(success=True, pig=current_pig_state(user, unlocked))

    @app.get('/api/me/stats')
    def my_stats():
        user = current_user()
        if user is None:
            abort(401, description='Sign in to view your focus history.')
        clients = db.session.scalars(db.select(ClientInstallation.client_id).where(
            ClientInstallation.user_id == user.id)).all()
        return stats_for_clients(clients)

    def stats_for_clients(clients):
        sessions = db.session.scalars(db.select(FocusSession).where(FocusSession.client_id.in_(clients)).order_by(FocusSession.started_at.desc())).all()
        finished = [s for s in sessions if s.ended_at is not None]
        scores = [s.focus_score for s in finished if s.focus_score is not None]
        days = defaultdict(float)
        for s in finished:
            days[as_utc(s.started_at).date().isoformat()] += s.actual_minutes or 0
        domains = Counter(a.domain for s in sessions for a in s.attempts)
        total = sum(s.actual_minutes or 0 for s in finished)
        def iso(value):
            return as_utc(value).isoformat().replace('+00:00', 'Z') if value else None
        user = current_user()
        pig = room_state(sessions, db.session.get(PigProfile, user.id), zone=request.args.get('timezone'))
        return jsonify(pig=pig, total_focus_minutes=total, total_sessions=len(sessions),
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
        client_id = request.args.get('client_id')
        if client_id is not None and not valid_client_id(client_id):
            abort(400, description='This dashboard link has an invalid installation ID. Open it from your extension.')
        user = current_user()
        if user is None:
            if client_id and auth_configured():
                login_session['pending_client_id'] = client_id
            return redirect(url_for('auth.login'))
        if client_id:
            claim_client(client_id, user)
            return redirect(url_for('dashboard'))
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
