import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from cachelib import SimpleCache
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from models import db, User, ClientInstallation, FocusSession, PigProfile
from pig_room import room_state
from pig_shop import ITEMS, LEGACY_ITEMS, ITEM_BY_ID, shop_calendar, season_active, equip_selection

NOW = datetime(2026, 10, 5, 12, tzinfo=timezone.utc)
CLIENT = '7b72a384-e915-4b92-8d8e-15c25e8157f8'


def study(minutes=25, score=75, day=0, completed=True, sid=1):
    return SimpleNamespace(id=sid, actual_minutes=minutes, focus_score=score,
                           blocked_count=0, completed=completed,
                           started_at=NOW-timedelta(days=day, minutes=minutes),
                           ended_at=NOW-timedelta(days=day))


def by_id(state):
    return {item['id']: item for item in state['items']}


class ShopRulesTest(unittest.TestCase):
    def test_shared_svg_assets_are_valid_and_independent(self):
        templates=Path(__file__).resolve().parents[1]/'templates'
        svg=(templates/'pig_room.html').read_text().replace("{% include 'pig.html' %}", (templates/'pig.html').read_text())
        root=ET.fromstring(svg)
        parents={child:node for node in root.iter() for child in node}
        sources=[node for node in root.iter() if 'data-pig-item' in node.attrib or 'data-pig-base' in node.attrib]
        self.assertEqual(len(sources),len({node.attrib.get('data-pig-item',node.attrib.get('data-pig-base')) for node in sources}))
        self.assertTrue({item['asset'] for item in ITEMS} <= {node.attrib.get('data-pig-item',node.attrib.get('data-pig-base')) for node in sources})
        for node in sources:
            parent=parents.get(node)
            while parent is not None:
                self.assertNotIn('data-pig-item',parent.attrib)
                parent=parents.get(parent)

    def test_rotation_week_boundaries_return_and_uniqueness(self):
        first = shop_calendar(NOW)
        for day in range(7):
            self.assertEqual(shop_calendar(NOW+timedelta(days=day))['weekly_ids'], first['weekly_ids'])
        second = shop_calendar(NOW+timedelta(days=7))
        self.assertNotEqual(first['weekly_ids'], second['weekly_ids'])
        self.assertEqual(len(first['weekly_ids']), 4)
        self.assertEqual(len(set(first['weekly_ids'])), 4)
        self.assertEqual(shop_calendar(NOW+timedelta(weeks=6))['weekly_ids'], first['weekly_ids'])
        self.assertEqual(shop_calendar(datetime(2027,1,1,tzinfo=timezone.utc))['week_key'], '2026-W53')
        self.assertEqual(first['week_key'], '2026-W41')
        self.assertEqual(first['next_rotation'], '2026-10-12')
        # Shared UTC means the same instant cannot produce different user rotations.
        self.assertEqual(shop_calendar(NOW.astimezone(timezone(timedelta(hours=-10)))), first)
        self.assertNotEqual(shop_calendar(datetime(2026,10,11,23,59,tzinfo=timezone.utc))['weekly_ids'],
                            shop_calendar(datetime(2026,10,12,tzinfo=timezone.utc))['weekly_ids'])

    def test_season_boundaries(self):
        for season, dates in {
            'october': [('2026-09-30', False), ('2026-10-01', True), ('2026-10-31', True), ('2026-11-01', False)],
            'winter': [('2026-11-30', False), ('2026-12-01', True), ('2027-02-28', True), ('2027-03-01', False)],
            'valentine': [('2026-01-31', False), ('2026-02-01', True), ('2026-02-14', True), ('2026-02-15', False)],
            'spring': [('2026-02-28', False), ('2026-03-01', True), ('2026-05-31', True), ('2026-06-01', False)]
        }.items():
            for value, expected in dates:
                self.assertEqual(season_active(season, datetime.fromisoformat(value).date()), expected)
        empty = room_state([], now=NOW)
        self.assertNotIn('keepsakes', [s['id'] for s in empty['shop']['sections']])
        feb = room_state([], now=datetime(2026,2,5,tzinfo=timezone.utc))
        self.assertTrue(by_id(feb)['mug_cocoa']['available'])
        self.assertTrue(by_id(feb)['rug_heart']['available'])

    def test_milestone_thresholds_and_ineligible_sessions(self):
        for item_id, below, reached in [
            ('star_glasses', [study(score=94)], [study(score=95)]),
            ('blanket', [study(minutes=59)], [study(minutes=60)]),
            ('rug_cloud', [study(minutes=299)], [study(minutes=300)]),
            ('vase', [study(day=i,sid=i) for i in range(2)], [study(day=i,sid=i) for i in range(3)]),
            ('pennant', [study(sid=i) for i in range(4)], [study(sid=i) for i in range(5)]),
        ]:
            self.assertFalse(by_id(room_state(below, now=NOW))[item_id]['owned'], item_id)
            earned = by_id(room_state(reached, now=NOW))[item_id]
            self.assertTrue(earned['owned'], item_id)
            self.assertFalse(earned['can_buy'])
        early = study(480,100,completed=False)
        self.assertFalse(by_id(room_state([early], now=NOW))['star_glasses']['owned'])
        running = study(480,100); running.ended_at = None
        self.assertFalse(by_id(room_state([running], now=NOW))['blanket']['owned'])
        # Same-day sessions do not count as three days.
        self.assertFalse(by_id(room_state([study(sid=i) for i in range(3)], now=NOW))['vase']['owned'])

    def test_legacy_and_owned_unavailable_items_are_preserved(self):
        legacy_ids = {item['id'] for item in LEGACY_ITEMS}
        self.assertEqual(len(legacy_ids), 12)
        self.assertEqual(len(ITEMS), len({item['id'] for item in ITEMS}))
        for months in [1,2,3,7,10,12]:
            state = room_state([], now=NOW.replace(month=months))
            self.assertTrue(all(by_id(state)[key]['available'] for key in legacy_ids))
        weekly = shop_calendar(NOW)['weekly_ids'][0]
        profile = SimpleNamespace(purchased_items=['mug','plant','mug_ghost',weekly],
                                  equipped_items=['mug_ghost','plant',weekly], coins_spent=120)
        future = room_state([study(minutes=480)], profile, now=NOW+timedelta(weeks=4))
        self.assertEqual(future['coins'], 360)
        self.assertTrue(by_id(future)[weekly]['owned'])
        self.assertTrue(by_id(future)['mug_ghost']['owned'])
        self.assertFalse(by_id(future)['mug_ghost']['available'])
        self.assertTrue(by_id(future)['mug_ghost']['visible'])
        self.assertEqual(by_id(future)['mug_ghost']['section'], 'keepsakes')
        self.assertEqual(set(future['equipped_items']), set(profile.equipped_items))

    def test_variants_share_slot_without_removing_other_equipment(self):
        self.assertEqual(equip_selection(['bow','headphones','mug'], 'bow_lavender'), ['bow_lavender','headphones','mug'])
        self.assertEqual(equip_selection(['bow_lavender','headphones'], 'bow'), ['bow','headphones'])
        self.assertEqual(equip_selection(['glasses','lamp'], 'star_glasses'), ['lamp','star_glasses'])
        self.assertEqual(equip_selection(['rug_checker','plant'], 'rug_cloud'), ['plant','rug_cloud'])


class ShopAPITest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING':True, 'SQLALCHEMY_DATABASE_URI':'sqlite://',
                              'SECRET_KEY':'shop-test-only', 'SESSION_CACHELIB':SimpleCache()})
        self.context=self.app.app_context(); self.context.push(); db.create_all()
        user=User(google_sub='shop-owner'); other=User(google_sub='other-shop-owner')
        db.session.add_all([user,other]); db.session.flush(); self.uid=user.id; self.other_id=other.id
        db.session.add(ClientInstallation(client_id=CLIENT,user_id=self.uid))
        db.session.add(FocusSession(client_id=CLIENT, task='Study', planned_minutes=360,
            actual_minutes=360, focus_score=75, completed=True,
            started_at=NOW-timedelta(minutes=360), ended_at=NOW))
        db.session.commit()
        self.client=self.viewer(self.uid); self.other=self.viewer(self.other_id)
        self.clock=patch('pig_shop.datetime', wraps=datetime); self.date=self.clock.start(); self.date.now.return_value=NOW

    def tearDown(self):
        self.clock.stop(); db.session.remove(); db.drop_all(); db.engine.dispose(); self.context.pop()

    def viewer(self, uid):
        viewer=self.app.test_client()
        with viewer.session_transaction() as session:
            session['user_id']=uid; session['csrf_token']='shop-token'
        return viewer

    def post(self, action, item_id, equipped=None, viewer=None):
        data={'item_id':item_id}
        if equipped is not None: data['equipped']=equipped
        return (viewer or self.client).post('/api/me/pig/'+action,json=data,headers={'X-CSRF-Token':'shop-token'})

    def state(self):
        response=self.client.get('/api/me/pig'); self.assertEqual(response.status_code,200)
        return response.json['pig']

    def test_weekly_purchase_then_rotation_and_retry(self):
        before=self.state(); current=before['shop']['weekly_ids'][0]
        hidden=next(item for item in before['items'] if item['kind']=='weekly' and not item['available'])
        self.assertEqual(self.post('unlock',hidden['id']).status_code,400)
        bought=self.post('unlock',current); self.assertEqual(bought.status_code,200)
        remaining=360-ITEM_BY_ID[current]['cost']
        self.date.now.return_value=NOW+timedelta(days=7)
        after=self.state()
        self.assertFalse(by_id(after)[current]['available'])
        self.assertTrue(by_id(after)[current]['visible'])
        self.assertEqual(self.post('equip',current,True).status_code,200)
        self.assertEqual(self.post('unlock',current).json['pig']['coins'],remaining)
        db.session.remove()
        self.assertIn(current,self.state()['equipped_items'])
        self.assertEqual(db.session.get(PigProfile,self.uid).purchased_items,[current])

    def test_seasonal_ownership_after_end_and_block_offseason_purchase(self):
        self.assertEqual(self.post('unlock','mug_ghost').status_code,200)
        self.post('equip','mug_ghost',True)
        self.date.now.return_value=NOW.replace(month=11)
        self.assertEqual(self.post('equip','mug_ghost',True).status_code,200)
        self.assertEqual(self.post('unlock','mug_ghost').json['pig']['coins'],270)
        self.assertEqual(self.post('unlock','plant_tulip').status_code,400)
        self.assertTrue(by_id(self.state())['mug_ghost']['equipped'])

    def test_milestones_cannot_be_bought_or_equipped_early(self):
        self.assertEqual(self.post('unlock','star_glasses').status_code,400)
        self.assertEqual(self.post('equip','star_glasses',True).status_code,400)
        study_row=db.session.scalar(db.select(FocusSession)); study_row.focus_score=95; db.session.commit()
        self.assertEqual(self.post('equip','star_glasses',True).status_code,200)
        self.assertEqual(self.state()['coins'],360)
        self.assertEqual(db.session.get(PigProfile,self.uid).purchased_items,[])

    def test_rare_affordability_no_duplicate_and_user_isolation(self):
        self.assertEqual(self.post('unlock','computer_strawberry').status_code,400)
        for i in range(2):
            db.session.add(FocusSession(client_id=CLIENT, task='Long study', planned_minutes=480,
                actual_minutes=480, completed=True, ended_at=NOW, started_at=NOW-timedelta(days=i+1)))
        db.session.commit()
        self.assertEqual(self.post('unlock','plushie').status_code,200)
        self.assertEqual(self.post('unlock','plushie').json['pig']['coins'],420)
        self.assertEqual(self.post('equip','plushie',True).status_code,200)
        self.assertEqual(self.post('equip','plushie',True,viewer=self.other).status_code,400)
        self.assertEqual(self.post('unlock','plushie',viewer=self.other).status_code,400)
        self.assertFalse(by_id(self.other.get('/api/me/pig').json['pig'])['plushie']['owned'])
        self.assertIn('plushie',self.state()['equipped_items'])
        self.assertEqual(self.app.test_client().get('/api/me/pig').status_code,401)

    def test_old_inventory_and_slot_replacement_preserve_spending(self):
        db.session.add(FocusSession(client_id=CLIENT, task='More XP', planned_minutes=90, actual_minutes=90, completed=True, started_at=NOW-timedelta(days=1), ended_at=NOW-timedelta(days=1)))
        profile=PigProfile(user_id=self.uid, purchased_items=['mug','plant','lamp'],
                           equipped_items=['bow','headphones','mug','plant','lamp'], coins_spent=135)
        db.session.add(profile); db.session.commit()
        before=self.state()
        self.assertEqual(before['coins'],315)
        self.assertTrue({'bow','headphones','mug','plant','lamp'} <= set(before['equipped_items']))
        self.date.now.return_value=NOW+timedelta(weeks=2)  # Lavender Bow rotates into this week.
        if not by_id(self.state())['bow_lavender']['available']:
            self.date.now.return_value=NOW+timedelta(weeks=3)
        self.assertEqual(self.post('unlock','bow_lavender').status_code,200)
        state=self.post('equip','bow_lavender',True).json['pig']
        self.assertNotIn('bow',state['equipped_items'])
        self.assertIn('bow_lavender',state['equipped_items'])
        self.assertTrue({'headphones','mug','plant','lamp'} <= set(state['equipped_items']))
        self.assertEqual(state['coins'],225)
        self.assertTrue({'mug','plant','lamp','bow_lavender'} <= set(db.session.get(PigProfile,self.uid).purchased_items))


if __name__=='__main__': unittest.main()
