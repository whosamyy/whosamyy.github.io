"""Google sign-in and dashboard ownership. Extension writes remain anonymous."""
import secrets
import time
from uuid import UUID
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from models import db, User, ClientInstallation

auth = Blueprint('auth', __name__)


def valid_client_id(value):
    try:
        parsed = UUID(value)
        return parsed.version == 4 and str(parsed) == value
    except (ValueError, TypeError, AttributeError):
        return False


def auth_configured():
    return all(current_app.config.get(key) for key in
               ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SECRET_KEY'))


def current_user():
    if not current_app.config.get('SECRET_KEY'):
        return None
    user_id = session.get('user_id')
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        return None
    user = db.session.get(User, user_id)
    if user is None:
        session.clear()
    return user


def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']


def claim_client(client_id, user):
    if not valid_client_id(client_id):
        abort(400, description='This dashboard link has an invalid installation ID. Open it from your extension.')
    installation = db.session.scalar(db.select(ClientInstallation).where(
        ClientInstallation.client_id == client_id))
    if installation is None:
        try:
            # Unique client_id + a savepoint make simultaneous claims safe.
            with db.session.begin_nested():
                installation = ClientInstallation(client_id=client_id, user_id=user.id)
                db.session.add(installation)
                db.session.flush()
            db.session.commit()
        except IntegrityError:
            installation = db.session.scalar(db.select(ClientInstallation).where(
                ClientInstallation.client_id == client_id))
            if installation is None:
                raise
    if installation.user_id != user.id:
        abort(403, description='This installation is linked to another account. Sign in with its owner’s account.')


def init_auth(app):
    oauth = OAuth(app)
    oauth.register('google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid', 'code_challenge_method': 'S256', 'timeout': 10})
    app.extensions['lock_oauth'] = oauth
    app.register_blueprint(auth)
    app.jinja_env.globals['csrf_token'] = csrf_token


@auth.get('/login')
def login():
    if current_user():
        return redirect(url_for('dashboard'))
    configured = auth_configured()
    return render_template('login.html', configured=configured), 200 if configured else 503


@auth.get('/auth/google')
def google():
    if not auth_configured():
        return render_template('login.html', configured=False), 503
    if current_user():
        return redirect(url_for('dashboard'))
    pending = session.get('pending_client_id')
    session.clear()
    session['oauth_started_at'] = time.time()
    if pending:
        session['pending_client_id'] = pending
    current_app.session_interface.regenerate(session)
    try:
        return current_app.extensions['lock_oauth'].google.authorize_redirect(
            current_app.config['OAUTH_REDIRECT_URI'])
    except Exception as error:
        # Do not log provider responses, credentials, authorization codes, or tokens.
        current_app.logger.warning('OAuth initiation failed: %s', type(error).__name__)
        session.clear()
        return render_template('auth_error.html', message='Google sign-in is temporarily unavailable. Please try again.'), 503


@auth.get('/auth/callback')
def callback():
    if not auth_configured():
        return render_template('login.html', configured=False), 503
    if current_user():
        # An unsolicited callback must not revoke an existing valid login.
        return redirect(url_for('dashboard'))
    pending = session.get('pending_client_id')
    started = session.get('oauth_started_at', 0)
    if not isinstance(started, (int, float)) or not 0 <= time.time() - started <= 600:
        session.clear()
        return render_template('auth_error.html', message='Your sign-in expired. Open your extension’s dashboard link and try again.'), 400
    try:
        # Authlib validates OAuth state and the ID token signature, issuer,
        # audience, expiry and OIDC nonce before returning userinfo.
        token = current_app.extensions['lock_oauth'].google.authorize_access_token()
        userinfo = token.get('userinfo')
        sub = userinfo.get('sub') if isinstance(userinfo, dict) else None
        if not isinstance(sub, str) or not sub or len(sub) > 255:
            raise ValueError('Missing Google subject')
    except Exception as error:
        current_app.logger.warning('OAuth callback rejected: %s', type(error).__name__)
        session.clear()
        message = ('Google sign-in was cancelled. Open your extension’s dashboard link to try again.'
                   if request.args.get('error') == 'access_denied' else
                   'Could not complete Google sign-in. Open your extension’s dashboard link to try again.')
        return render_template('auth_error.html', message=message), 400
    user = db.session.scalar(db.select(User).where(User.google_sub == sub))
    if user is None:
        try:
            with db.session.begin_nested():
                user = User(google_sub=sub)
                db.session.add(user)
                db.session.flush()
            db.session.commit()
        except IntegrityError:
            user = db.session.scalar(db.select(User).where(User.google_sub == sub))
            if user is None:
                raise
    session.clear()
    session['user_id'] = user.id
    session.permanent = True
    current_app.session_interface.regenerate(session)
    if pending:
        claim_client(pending, user)
    return redirect(url_for('dashboard'))


@auth.post('/logout')
def logout():
    expected = session.get('csrf_token')
    supplied = request.form.get('csrf_token', '')
    if not expected or not secrets.compare_digest(expected, supplied):
        abort(403, description='Please reload your dashboard before signing out.')
    session.clear()
    return redirect(url_for('auth.login'))
