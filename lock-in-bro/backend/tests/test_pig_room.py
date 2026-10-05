import sys
import math
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from cachelib import SimpleCache
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from models import db, User, ClientInstallation, FocusSession, PigProfile
from pig_room import determine_pig_mood, determine_focus_weather, earned_coins, MESSAGES, room_state

NOW = datetime(2026, 10, 5, 16, tzinfo=timezone.utc)
CLIENT = '7b72a384-e915-4b92-8d8e-15c25e8157f8'


def focus(score=75, blocked=1, minutes=25, completed=True, hours=0, sid=1):
    return SimpleNamespace(id=sid, focus_score=score, blocked_count=blocked,
                           actual_minutes=minutes, completed=completed,
                           started_at=NOW - timedelta(hours=hours, minutes=minutes if math.isfinite(minutes) else 0),
                           ended_at=NOW - timedelta(hours=hours))


class AtmosphereTest(unittest.TestCase):
    def test_all_moods_messages_and_priority(self):
        cases = [([], 'sleepy'), ([focus()], 'happy'), ([focus(score=95)], 'proud'),
                 ([focus(score=60)], 'cozy'), ([focus(minutes=3)], 'sleepy'),
                 ([focus(blocked=6, score=95)], 'distracted'),
                 ([focus(hours=49)], 'sleepy'), ([focus(minutes=90)], 'excited')]
        for sessions, mood in cases:
            with self.subTest(mood=mood):
                result = room_state(sessions, now=NOW)
                self.assertEqual(result['mood'], mood)
                self.assertEqual(result['message'], MESSAGES[mood])
        self.assertEqual(determine_pig_mood([focus(blocked=9)], NOW, unlocked_something=True), 'excited')
        self.assertEqual(determine_pig_mood([focus(score=50, minutes=10, sid=i) for i in range(3)], NOW), 'proud')
        self.assertEqual(determine_pig_mood([focus(sid=i, score=50, minutes=5) for i in range(5)], NOW), 'excited')
        running = focus(); running.ended_at = None
        self.assertEqual(determine_pig_mood([running], NOW), 'sleepy')
        self.assertEqual(determine_pig_mood([focus(hours=-1)], NOW), 'sleepy')

    def test_weather_priority_and_local_night(self):
        cases = [([], 'cloudy'), ([focus(score=95)], 'sunny'), ([focus()], 'cloudy'),
                 ([focus(blocked=6, score=95)], 'rainy'), ([focus(score=40)], 'rainy'),
                 ([focus(score=99)], 'sparkle'), ([focus(minutes=90)], 'sparkle')]
        for sessions, weather in cases:
            self.assertEqual(determine_focus_weather(sessions, NOW), weather)
        night = focus(hours=17, score=95, blocked=8)
        self.assertEqual(determine_focus_weather([night], NOW), 'night')
        self.assertEqual(determine_focus_weather([night], NOW, unlocked_something=True), 'sparkle')
        self.assertEqual(determine_pig_mood([focus()], NOW, zone='Asia/Tokyo'), 'sleepy')
        self.assertEqual(determine_focus_weather([focus(score=95)], NOW, zone='Asia/Tokyo'), 'night')
        self.assertEqual(room_state([], zone='Not/AZone')['timezone'], 'UTC')
        naive = focus(); naive.started_at = naive.started_at.replace(tzinfo=None); naive.ended_at = naive.ended_at.replace(tzinfo=None)
        self.assertEqual(determine_pig_mood([naive], NOW), 'happy')

    def test_coin_rules(self):
        self.assertEqual(earned_coins([focus(minutes=25.9), focus(completed=False)]), 25)
        self.assertEqual(earned_coins([focus(minutes=float('nan')), focus(minutes=-1)]), 0)
        self.assertEqual(earned_coins([focus(minutes=999)]), 480)


class RoomAPITest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://',
                              'SECRET_KEY': 'room-test-only', 'SESSION_CACHELIB': SimpleCache()})
        self.context = self.app.app_context(); self.context.push(); db.create_all()
        user = User(google_sub='room-owner'); other = User(google_sub='other-owner')
        db.session.add_all([user, other]); db.session.flush()
        self.uid, self.other_id = user.id, other.id
        db.session.add(ClientInstallation(client_id=CLIENT, user_id=user.id))
        db.session.add(FocusSession(client_id=CLIENT, task='Read', planned_minutes=150,
                                   actual_minutes=150, focus_score=95, blocked_count=0,
                                   started_at=NOW-timedelta(minutes=150), ended_at=NOW, completed=True))
        db.session.commit()
        self.client = self.viewer(self.uid)
        self.other = self.viewer(self.other_id)

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.context.pop()

    def viewer(self, uid):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session['user_id'] = uid; session['csrf_token'] = 'room-test-token'
        return client

    def post(self, action, data, client=None):
        return (client or self.client).post('/api/me/pig/' + action, json=data,
                                           headers={'X-CSRF-Token': 'room-test-token'})

    def test_unlock_equip_unequip_and_persistence(self):
        initial = self.client.get('/api/me/pig').json['pig']
        self.assertEqual(initial['coins'], 150)
        self.assertEqual(len(initial['items']), 12)
        self.assertIn('sparkles', initial['equipped_items'])
        bought = self.post('unlock', {'item_id': 'plant'})
        self.assertEqual(bought.status_code, 200)
        self.assertEqual(bought.json['pig']['coins'], 100)
        self.assertEqual(bought.json['pig']['mood'], 'excited')
        self.assertEqual(bought.json['pig']['weather'], 'sparkle')
        self.assertEqual(bought.json['pig']['message'], 'NEW ITEM UNLOCKED!! ✨')
        self.assertNotIn('plant', bought.json['pig']['equipped_items'])
        self.assertEqual(self.post('unlock', {'item_id': 'plant'}).json['pig']['coins'], 100)
        equipped = self.post('equip', {'item_id': 'plant', 'equipped': True})
        self.assertIn('plant', equipped.json['pig']['equipped_items'])
        db.session.remove()
        another_browser = self.viewer(self.uid)
        self.assertIn('plant', another_browser.get('/api/me/stats').json['pig']['equipped_items'])
        self.assertEqual(db.session.get(PigProfile, self.uid).purchased_items, ['plant'])
        self.post('equip', {'item_id': 'plant', 'equipped': False})
        self.assertNotIn('plant', self.client.get('/api/me/pig').json['pig']['equipped_items'])
        self.assertEqual(self.client.get('/api/me/stats').json['total_focus_minutes'], 150)
        self.assertEqual(db.session.query(FocusSession).count(), 1)

    def test_locked_insufficient_invalid_csrf_and_ownership(self):
        self.assertEqual(self.post('equip', {'item_id': 'lamp', 'equipped': True}).status_code, 400)
        self.assertEqual(self.post('unlock', {'item_id': 'bow'}).status_code, 400)
        self.assertEqual(self.post('unlock', {'item_id': 'plant'}, self.other).status_code, 400)
        self.assertEqual(self.post('equip', {'item_id': 'plant', 'equipped': True, 'user_id': self.uid}, self.other).status_code, 400)
        self.assertEqual(self.post('equip', {'item_id': 'plant', 'equipped': True}, self.other).status_code, 400)
        self.assertEqual(self.client.post('/api/me/pig/unlock', json={'item_id': 'plant'}).status_code, 403)
        self.assertEqual(self.client.post('/api/me/pig/unlock', json={'item_id': 'plant'}, headers={'X-CSRF-Token': '☕'}).status_code, 403)
        for path in ['unlock', 'equip']:
            self.assertEqual(self.app.test_client().post('/api/me/pig/'+path, json={'item_id':'plant'}).status_code, 401)
        self.assertEqual(self.app.test_client().get('/api/me/pig').status_code, 401)
        for data in [[], {'item_id': []}, {'item_id': 'fake'}, {'item_id': 'laptop', 'equipped': 'yes'}]:
            self.assertEqual(self.post('equip', data).status_code, 400)
        self.post('unlock', {'item_id': 'lights'})
        self.post('unlock', {'item_id': 'lamp'})
        self.assertEqual(self.client.get('/api/me/pig').json['pig']['coins'], 10)
        self.assertEqual(self.post('unlock', {'item_id': 'plant'}).status_code, 400)
        self.assertEqual(self.other.get('/api/me/pig').json['pig']['coins'], 0)
        self.assertNotIn('lights', self.other.get('/api/me/pig').json['pig']['equipped_items'])

    def test_empty_equipment_stays_empty_and_read_does_not_write(self):
        state = self.client.get('/api/me/pig').json['pig']
        self.assertEqual(db.session.query(PigProfile).count(), 0)
        for item in state['equipped_items']:
            self.post('equip', {'item_id': item, 'equipped': False})
        self.assertEqual(self.client.get('/api/me/pig').json['pig']['equipped_items'], [])
        db.session.remove()
        self.assertEqual(self.client.get('/api/me/pig').json['pig']['equipped_items'], [])

    def test_profile_json_validation(self):
        for value in ['plant', ['fake'], [42], {'plant': True}]:
            with self.assertRaises(ValueError):
                PigProfile(user_id=self.uid, purchased_items=value)
            with self.assertRaises(ValueError):
                PigProfile(user_id=self.uid, equipped_items=value)
        with self.assertRaises(ValueError):
            PigProfile(user_id=self.uid, purchased_items=['bow'])
        self.assertEqual(PigProfile(user_id=self.uid, equipped_items=['plant', 'plant']).equipped_items, ['plant'])

    def test_additive_init_preserves_history_and_accounts(self):
        PigProfile.__table__.drop(db.engine)
        result = self.app.test_cli_runner().invoke(args=['init-db'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(db.session.query(User).count(), 2)
        self.assertEqual(db.session.query(FocusSession).count(), 1)
        self.assertEqual(self.client.get('/api/me/pig').json['pig']['coins'], 150)


class ConcurrentPurchaseTest(unittest.TestCase):
    def test_duplicate_purchase_spends_once(self):
        with tempfile.TemporaryDirectory() as directory:
            app = create_app({'TESTING': True, 'SECRET_KEY': 'concurrency-test',
                              'SESSION_CACHELIB': SimpleCache(),
                              'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + directory + '/test.db'})
            with app.app_context():
                db.create_all()
                user = User(google_sub='buyer'); db.session.add(user); db.session.flush(); uid = user.id
                db.session.add(ClientInstallation(user_id=uid, client_id=CLIENT))
                db.session.add(FocusSession(client_id=CLIENT, task='Read', planned_minutes=50,
                    actual_minutes=50, completed=True, ended_at=NOW))
                db.session.commit()
            def purchase(_):
                client = app.test_client()
                with client.session_transaction() as session:
                    session['user_id'] = uid; session['csrf_token'] = 'token'
                return client.post('/api/me/pig/unlock', json={'item_id': 'plant'}, headers={'X-CSRF-Token':'token'}).status_code
            with ThreadPoolExecutor(max_workers=2) as pool:
                self.assertEqual(list(pool.map(purchase, range(2))), [200, 200])
            with app.app_context():
                profile = db.session.get(PigProfile, uid)
                self.assertEqual(profile.coins_spent, 50)
                self.assertEqual(profile.purchased_items, ['plant'])
                db.session.remove(); db.engine.dispose()


if __name__ == '__main__': unittest.main()
