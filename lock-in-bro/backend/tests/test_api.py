import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from models import db, BlockedAttempt
from models import User, ClientInstallation
from cachelib import SimpleCache

class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://',
                               'SECRET_KEY': 'test-only-key', 'SESSION_CACHELIB': SimpleCache()})
        self.context = self.app.app_context(); self.context.push()
        db.create_all(); self.client = self.app.test_client()
        self.payload = dict(client_id='7b72a384-e915-4b92-8d8e-15c25e8157f8', task='Probability', planned_minutes=45,
                            blocked_domains=['reddit.com'], started_at='2026-09-30T12:00:00Z')
        user = User(google_sub='test-sub'); db.session.add(user); db.session.flush()
        db.session.add(ClientInstallation(client_id=self.payload['client_id'], user_id=user.id)); db.session.commit()
        self.viewer = self.app.test_client()
        with self.viewer.session_transaction() as session: session['user_id'] = user.id
    def tearDown(self):
        db.session.remove(); db.drop_all(); self.context.pop()
    def test_lifecycle(self):
        self.assertEqual(self.client.get('/api/health').status_code, 200)
        result = self.client.post('/api/sessions', json=self.payload)
        self.assertEqual(result.status_code, 201)
        sid = result.json['session_id']
        self.assertEqual(self.client.post(f'/api/sessions/{sid}/blocked', json={'domain':'reddit.com','timestamp':'2026-09-30T12:02:00Z'}).status_code, 201)
        self.assertEqual(db.session.query(BlockedAttempt).count(), 1)
        finish = dict(ended_at='2026-09-30T12:43:30Z',completed=False,actual_minutes=43.5,blocked_count=2,focus_score=None)
        for _ in range(2):
            self.assertEqual(self.client.post(f'/api/sessions/{sid}/finish',json=finish).status_code,200)
        stats = self.viewer.get('/api/me/stats').json
        self.assertEqual(stats['total_focus_minutes'],43.5)
        self.assertEqual(stats['total_blocked_attempts'],2)
        self.assertEqual(stats['completed_sessions'],0)
        self.assertIsNone(stats['average_focus_score'])
        self.assertEqual(stats['most_blocked_domains'],[{'domain':'reddit.com','count':1}])
        self.assertEqual(stats['focus_by_day'],[{'day':'2026-09-30','minutes':43.5}])
        self.assertEqual(self.viewer.get('/').status_code,200)
        self.assertEqual(self.client.get('/api/me/stats').status_code,401)
    def test_invalid(self):
        self.assertEqual(self.client.post('/api/sessions',data='{',content_type='application/json').status_code,400)
        for key,value in [('client_id',''),('task',''),('planned_minutes',True),('planned_minutes',0),('planned_minutes',481),('blocked_domains',['https://reddit.com/private']),('started_at','yesterday')]:
            self.assertEqual(self.client.post('/api/sessions',json={**self.payload,key:value}).status_code,400)
        self.assertEqual(self.client.post('/api/sessions/999/finish',json={}).status_code,404)
        sid=self.client.post('/api/sessions',json=self.payload).json['session_id']
        for data in [{},{'domain':'example.com','timestamp':'2026-09-30T12:01:00Z'},{'domain':'reddit.com','timestamp':'bad'}]:
            self.assertEqual(self.client.post(f'/api/sessions/{sid}/blocked',json=data).status_code,400)
    def test_start_retry_reuses_session(self):
        first = self.client.post('/api/sessions', json=self.payload)
        retry = self.client.post('/api/sessions', json=self.payload)
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(retry.json['session_id'], first.json['session_id'])
        self.assertEqual(self.viewer.get('/api/me/stats').json['total_sessions'], 1)
    def test_database_failure(self):
        db.drop_all()
        result=self.viewer.get('/api/me/stats')
        self.assertEqual(result.status_code,503)
        self.assertEqual(result.json['error'],'Database unavailable. Please try again.')

if __name__ == '__main__': unittest.main()
