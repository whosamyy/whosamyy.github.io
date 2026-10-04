import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
from cachelib import SimpleCache
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pig import pig_progress
from app import create_app
from models import db, User, ClientInstallation, FocusSession

CLIENT = '7b72a384-e915-4b92-8d8e-15c25e8157f8'
SECOND = '420d50f5-572b-4245-adde-9c05d82b9ec6'


def finished(minutes=25, score=90, completed=True):
    return SimpleNamespace(actual_minutes=minutes, focus_score=score,
                           completed=completed, ended_at=datetime.now(timezone.utc))


class PigRewardTest(unittest.TestCase):
    def test_empty_and_ineligible_sessions(self):
        running = finished(); running.ended_at = None
        pig = pig_progress([running, finished(completed=False)])
        self.assertEqual((pig['total_xp'], pig['level'], pig['level_xp']), (0, 1, 0))
        self.assertEqual(pig['unlocked_items'], [])
        self.assertEqual(pig['next_unlock']['xp_remaining'], 100)

    def test_minutes_and_score_bonus(self):
        self.assertEqual(pig_progress([finished(25.9, 99.9)])['total_xp'], 44)
        self.assertEqual(pig_progress([finished(25, None)])['total_xp'], 35)
        self.assertEqual(pig_progress([finished(None, None)])['total_xp'], 10)
        self.assertEqual(pig_progress([finished(float('nan'), float('inf'))])['total_xp'], 10)

    def test_thresholds_and_accessories(self):
        for total, level, items in [(99, 1, []), (100, 2, ['sparkles']),
                (200, 3, ['sparkles', 'bow']), (400, 5, ['sparkles', 'bow', 'headphones']),
                (600, 7, ['sparkles', 'bow', 'headphones', 'strawberry']),
                (900, 10, ['sparkles', 'bow', 'headphones', 'strawberry', 'glasses'])]:
            with self.subTest(total=total):
                sessions = [finished(90, None)] * (total // 100)
                if total % 100: sessions.append(finished(total % 100 - 10, None))
                pig = pig_progress(sessions)
                self.assertEqual(pig['level'], level)
                self.assertEqual(pig['total_xp'], total)
                self.assertEqual([item['id'] for item in pig['unlocked_items']], items)
        self.assertIsNone(pig['next_unlock'])

    def test_account_scope_all_history_and_persistence(self):
        app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://',
                          'SECRET_KEY': 'pig-test-only-key', 'SESSION_CACHELIB': SimpleCache()})
        with app.app_context():
            db.create_all()
            user = User(google_sub='pig-owner'); db.session.add(user); db.session.flush()
            owner_id = user.id
            db.session.add_all([ClientInstallation(client_id=c, user_id=user.id) for c in [CLIENT, SECOND]])
            for index in range(22):
                db.session.add(FocusSession(client_id=CLIENT if index % 2 else SECOND,
                    task='Study', planned_minutes=25, actual_minutes=25, focus_score=90,
                    completed=True, ended_at=datetime.now(timezone.utc)))
            db.session.add(FocusSession(client_id='unowned', task='Other account',
                planned_minutes=480, actual_minutes=480, completed=True,
                ended_at=datetime.now(timezone.utc), focus_score=100))
            db.session.commit()
            viewer = app.test_client()
            with viewer.session_transaction() as session: session['user_id'] = owner_id
            before = viewer.get('/api/me/stats').json
            self.assertEqual(before['pig']['total_xp'], 22 * 44)
            self.assertEqual(len(before['recent_sessions']), 20)
            self.assertEqual(before['completed_sessions'], 22)
            db.session.remove()
            self.assertEqual(viewer.get('/api/me/stats').json['pig'], before['pig'])
            self.assertEqual(viewer.get('/api/stats/' + CLIENT).json['pig']['total_xp'], 11 * 44)
            self.assertEqual(app.test_client().get('/api/me/stats').status_code, 401)
            db.session.remove(); db.drop_all(); db.engine.dispose()


if __name__ == '__main__': unittest.main()
