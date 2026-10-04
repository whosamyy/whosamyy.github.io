import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from cachelib import SimpleCache
from flask import redirect
from sqlalchemy import inspect
from authlib.integrations.base_client.errors import OAuthError
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from models import db, User, ClientInstallation, FocusSession, BlockedAttempt

CLIENT = '7b72a384-e915-4b92-8d8e-15c25e8157f8'
SECOND = '420d50f5-572b-4245-adde-9c05d82b9ec6'


class AuthTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'SECRET_KEY': 'test-only-secret', 'GOOGLE_CLIENT_ID': 'test-client',
            'GOOGLE_CLIENT_SECRET': 'test-secret', 'SESSION_CACHELIB': SimpleCache()})
        self.context = self.app.app_context(); self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.google = self.app.extensions['lock_oauth'].google

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.context.pop()

    def user(self, sub='google-sub-one', client=None):
        user = User(google_sub=sub); db.session.add(user); db.session.commit()
        viewer = client or self.client
        with viewer.session_transaction() as session:
            session['user_id'] = user.id
        return user

    def oauth_sign_in(self, sub='google-sub-one', pending=None, viewer=None):
        viewer = viewer or self.client
        if pending:
            self.assertEqual(viewer.get('/?client_id=' + pending).status_code, 302)
        with patch.object(self.google, 'authorize_redirect', return_value=redirect('/mock-google')) as start:
            self.assertEqual(viewer.get('/auth/google').status_code, 302)
            start.assert_called_once_with('http://127.0.0.1:5000/auth/callback')
        token = {'userinfo': {'sub': sub, 'email': 'not-stored@example.test', 'name': 'Not stored'},
                 'access_token': 'discard-this-token', 'id_token': 'discard-this-id-token'}
        with patch.object(self.google, 'authorize_access_token', return_value=token):
            return viewer.get('/auth/callback?code=mock')

    def write_session(self, client_id=CLIENT, start='2026-10-04T12:00:00Z', minutes=25):
        result = self.app.test_client().post('/api/sessions', json={
            'client_id': client_id, 'task': 'Existing private study', 'planned_minutes': minutes,
            'blocked_domains': ['reddit.com'], 'started_at': start})
        self.assertEqual(result.status_code, 201)
        sid = result.json['session_id']
        self.assertEqual(self.app.test_client().post(f'/api/sessions/{sid}/finish', json={
            'ended_at': '2026-10-04T13:00:00Z', 'completed': True,
            'actual_minutes': minutes, 'blocked_count': 2, 'focus_score': 90}).status_code, 200)
        return sid

    def test_logged_out_reads_and_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/login')
        login = self.client.get('/login')
        self.assertIn(b'Continue with Google', login.data)
        self.assertNotIn(b'RECENT SESSIONS', login.data)
        for path in ['/api/me/stats', '/api/stats/' + CLIENT]:
            self.assertEqual(self.client.get(path).status_code, 401)

    def test_oauth_claim_recovers_existing_history_and_minimizes_data(self):
        sid = self.write_session()
        response = self.oauth_sign_in(pending=CLIENT)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')
        self.assertEqual(self.client.get('/').status_code, 200)
        stats = self.client.get('/api/me/stats').json
        self.assertEqual(stats['total_focus_minutes'], 25)
        self.assertEqual(stats['recent_sessions'][0]['id'], sid)
        self.assertEqual(db.session.query(User).count(), 1)
        self.assertEqual(db.session.query(ClientInstallation).count(), 1)
        self.assertEqual(db.session.get(FocusSession, sid).client_id, CLIENT)
        self.assertEqual({c['name'] for c in inspect(db.engine).get_columns('user')},
                         {'id', 'google_sub', 'created_at'})
        with self.client.session_transaction() as session:
            self.assertEqual(set(session), {'user_id', '_permanent', 'csrf_token'})
        # Revisit and callback under the same Google account reuse ownership/user.
        self.assertEqual(self.client.get('/?client_id=' + CLIENT).location, '/')
        self.assertEqual(self.client.get('/api/stats/' + CLIENT).status_code, 200)
        other_browser = self.app.test_client()
        self.assertEqual(self.oauth_sign_in(viewer=other_browser).status_code, 302)
        self.assertEqual(db.session.query(User).count(), 1)
        self.assertEqual(other_browser.get('/api/me/stats').json['total_sessions'], 1)

    def test_claim_owner_and_reject_other_account(self):
        owner = self.user()
        self.assertEqual(self.client.get('/?client_id=' + CLIENT).status_code, 302)
        self.assertEqual(self.client.get('/?client_id=' + CLIENT).status_code, 302)
        intruder = self.app.test_client(); self.user('other-sub', intruder)
        response = intruder.get('/?client_id=' + CLIENT)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(CLIENT.encode(), response.data)
        self.assertEqual(intruder.get('/api/stats/' + CLIENT).status_code, 403)
        self.assertEqual(intruder.get('/api/me/stats').json['total_sessions'], 0)
        installation = db.session.scalar(db.select(ClientInstallation))
        self.assertEqual(installation.user_id, owner.id)

    def test_oauth_cannot_reassign_an_owned_client(self):
        self.user(); self.client.get('/?client_id=' + CLIENT)
        intruder = self.app.test_client()
        response = self.oauth_sign_in('another-google-sub', CLIENT, intruder)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(intruder.get('/api/stats/' + CLIENT).status_code, 403)

    def test_multiple_installations_aggregate_only_owned_history(self):
        self.write_session(CLIENT)
        self.write_session(SECOND, '2026-10-04T12:05:00Z', 45)
        self.write_session('c325f66b-77a7-4528-9944-b908dd5ca75a', '2026-10-04T12:06:00Z')
        self.user()
        for client in [CLIENT, SECOND]: self.client.get('/?client_id=' + client)
        stats = self.client.get('/api/me/stats').json
        self.assertEqual(stats['total_sessions'], 2)
        self.assertEqual(stats['total_focus_minutes'], 70)
        self.assertEqual(stats['completed_sessions'], 2)
        self.assertEqual(stats['total_blocked_attempts'], 4)
        self.assertEqual(stats['average_session_length'], 35)

    def test_missing_and_invalid_client_and_unowned_stats(self):
        self.assertEqual(self.client.get('/').status_code, 302)
        for value in ['', 'abc123', '../secret', '00000000-0000-0000-0000-000000000000', CLIENT.upper()]:
            self.assertEqual(self.client.get('/?client_id=' + value).status_code, 400)
        self.user()
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/api/me/stats').json['total_sessions'], 0)
        self.assertEqual(self.client.get('/api/stats/' + CLIENT).status_code, 403)
        self.assertEqual(self.client.get('/api/stats/invalid').status_code, 400)

    def test_logout_csrf_and_old_session_revocation(self):
        self.user(); self.client.get('/')
        cookie = self.client.get_cookie('lock_dashboard').value
        self.assertEqual(self.client.post('/logout').status_code, 403)
        with self.client.session_transaction() as session: csrf = session['csrf_token']
        response = self.client.post('/logout', data={'csrf_token': csrf})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get('/api/me/stats').status_code, 401)
        self.assertEqual(self.client.get('/').location, '/login')
        replay = self.app.test_client(); replay.set_cookie('lock_dashboard', cookie)
        self.assertEqual(replay.get('/api/me/stats').status_code, 401)

    def test_expired_and_deleted_user_sessions(self):
        user = self.user()
        db.session.delete(user); db.session.commit()
        self.assertEqual(self.client.get('/api/me/stats').status_code, 401)
        self.user('new-sub')
        self.app.config['SESSION_CACHELIB'].clear()
        self.assertEqual(self.client.get('/api/me/stats').status_code, 401)

    def test_google_cancelled_and_callback_error(self):
        for error, query in [(OAuthError(error='access_denied'), '?error=access_denied'),
                             (ValueError('secret provider response'), '?code=bad')]:
            with self.client.session_transaction() as session: session['oauth_started_at'] = time.time()
            with patch.object(self.google, 'authorize_access_token', side_effect=error):
                response = self.client.get('/auth/callback' + query)
            self.assertEqual(response.status_code, 400)
            self.assertNotIn(b'secret provider response', response.data)
            self.assertEqual(self.client.get('/api/me/stats').status_code, 401)
        self.assertEqual(db.session.query(User).count(), 0)

    def test_real_authlib_rejects_missing_state_without_network(self):
        # Exercise Authlib itself rather than mocking away state protection.
        with self.client.session_transaction() as session: session['oauth_started_at'] = time.time()
        with patch('requests.sessions.Session.request', side_effect=AssertionError('No network allowed')), \
             patch.object(self.google, 'fetch_access_token') as exchange:
            response = self.client.get('/auth/callback?code=forged&state=not-in-session')
            exchange.assert_not_called()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(db.session.query(User).count(), 0)

    def test_callback_without_flow_or_with_expired_flow(self):
        self.assertEqual(self.client.get('/auth/callback?code=mock').status_code, 400)
        with self.client.session_transaction() as session: session['oauth_started_at'] = time.time() - 601
        with patch.object(self.google, 'authorize_access_token') as exchange:
            self.assertEqual(self.client.get('/auth/callback?code=mock').status_code, 400)
            exchange.assert_not_called()

    def test_unsolicited_callback_does_not_log_out_signed_in_user(self):
        self.user()
        with patch.object(self.google, 'authorize_access_token') as exchange:
            self.assertEqual(self.client.get('/auth/callback?error=access_denied').status_code, 302)
            exchange.assert_not_called()
        self.assertEqual(self.client.get('/api/me/stats').status_code, 200)

    def test_real_oidc_validation_with_mock_provider(self):
        from urllib.parse import parse_qs, urlsplit
        from joserfc import jwt
        from joserfc.jwk import RSAKey
        key = RSAKey.generate_key(2048)
        public = key.as_dict(private=False); public['kid'] = 'test-key'
        metadata = {'issuer': 'https://accounts.google.com',
            'authorization_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_endpoint': 'https://oauth2.googleapis.com/token',
            'id_token_signing_alg_values_supported': ['RS256'],
            'code_challenge_methods_supported': ['S256']}
        for invalid in [None, 'nonce', 'aud', 'iss', 'expired', 'signature']:
            with self.subTest(invalid=invalid):
                viewer = self.app.test_client()
                with patch.object(self.google, 'load_server_metadata', return_value=metadata), \
                     patch.object(self.google, 'fetch_jwk_set', return_value={'keys': [public]}), \
                     patch('requests.sessions.Session.request', side_effect=AssertionError('No network allowed')):
                    response = viewer.get('/auth/google')
                    params = parse_qs(urlsplit(response.location).query)
                    self.assertEqual(params['scope'], ['openid'])
                    self.assertEqual(params['code_challenge_method'], ['S256'])
                    now = int(time.time())
                    claims = {'iss': metadata['issuer'], 'aud': 'test-client', 'sub': 'oidc-test-sub',
                              'iat': now, 'exp': now + 300, 'nonce': params['nonce'][0]}
                    if invalid == 'nonce': claims['nonce'] = 'wrong-nonce'
                    if invalid == 'aud': claims['aud'] = 'other-app'
                    if invalid == 'iss': claims['iss'] = 'https://attacker.example'
                    if invalid == 'expired': claims['iat'] = now - 1000; claims['exp'] = now - 600
                    signing_key = RSAKey.generate_key(2048) if invalid == 'signature' else key
                    encoded = jwt.encode({'alg': 'RS256', 'kid': 'test-key'}, claims, signing_key)
                    with patch.object(self.google, 'fetch_access_token', return_value={'id_token': encoded,
                            'access_token': 'ephemeral-test-token', 'token_type': 'Bearer'}) as exchange:
                        result = viewer.get('/auth/callback?code=mock&state=' + params['state'][0])
                    self.assertEqual(result.status_code, 302 if invalid is None else 400)
                    self.assertIn('code_verifier', exchange.call_args.kwargs)
                    self.assertEqual(viewer.get('/api/me/stats').status_code, 200 if invalid is None else 401)

    def test_missing_credentials_is_safe(self):
        for key in ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SECRET_KEY']:
            with patch.dict(self.app.config, {key: None}):
                self.assertEqual(self.app.test_client().get('/login').status_code, 503)
                self.assertEqual(self.app.test_client().get('/auth/google').status_code, 503)
                self.assertEqual(self.app.test_client().get('/auth/callback').status_code, 503)

    def test_provider_unavailable_and_missing_subject(self):
        with patch.object(self.google, 'authorize_redirect', side_effect=RuntimeError('secret error details')):
            response = self.client.get('/auth/google')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b'secret error details', response.data)
        with self.client.session_transaction() as session: session['oauth_started_at'] = time.time()
        with patch.object(self.google, 'authorize_access_token', return_value={'access_token': 'not-an-identity'}):
            self.assertEqual(self.client.get('/auth/callback').status_code, 400)
        self.assertEqual(db.session.query(User).count(), 0)

    def test_database_failure_no_analytics_or_trace(self):
        self.user(); db.drop_all()
        for path in ['/', '/api/me/stats']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 503)
            self.assertNotIn(b'Traceback', response.data)

    def test_scopes_and_session_fixation(self):
        self.assertEqual(self.google.client_kwargs['scope'], 'openid')
        self.client.get('/?client_id=' + CLIENT)
        old_cookie = self.client.get_cookie('lock_dashboard').value
        self.oauth_sign_in()
        self.assertNotEqual(old_cookie, self.client.get_cookie('lock_dashboard').value)
        replay = self.app.test_client(); replay.set_cookie('lock_dashboard', old_cookie)
        self.assertEqual(replay.get('/api/me/stats').status_code, 401)

    def test_init_db_preserves_existing_focus_and_attempt_rows(self):
        sid = self.write_session()
        from datetime import datetime, timezone
        attempt = BlockedAttempt(session_id=sid, domain='reddit.com',
                                 timestamp=datetime(2026, 10, 4, 12, 1, tzinfo=timezone.utc))
        db.session.add(attempt); db.session.commit(); attempt_id = attempt.id
        # Simulate deployment onto an existing Phase 2 database.
        ClientInstallation.__table__.drop(db.engine); User.__table__.drop(db.engine)
        result = self.app.test_cli_runner().invoke(args=['init-db'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIsNotNone(db.session.get(FocusSession, sid))
        self.assertIsNotNone(db.session.get(BlockedAttempt, attempt_id))
        self.assertIn('client_installation', inspect(db.engine).get_table_names())

    def test_render_https_cookie_and_callback(self):
        with patch.dict(os.environ, {'RENDER': 'true'}):
            app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://',
                'SECRET_KEY': 'test-only-secret', 'GOOGLE_CLIENT_ID': 'test-client',
                'GOOGLE_CLIENT_SECRET': 'test-secret', 'SESSION_CACHELIB': SimpleCache()})
        viewer = app.test_client()
        result = viewer.get('/?client_id=' + CLIENT, base_url='https://lock-in-bro.onrender.com')
        cookie = result.headers['Set-Cookie']
        for flag in ['Secure', 'HttpOnly', 'SameSite=Lax']: self.assertIn(flag, cookie)
        self.assertEqual(app.config['OAUTH_REDIRECT_URI'], 'https://lock-in-bro.onrender.com/auth/callback')
        self.assertEqual(viewer.get('/', base_url='https://attacker.example').status_code, 400)


if __name__ == '__main__': unittest.main()
