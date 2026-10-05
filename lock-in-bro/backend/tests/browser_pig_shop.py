"""Growing-shop QA with a temporary SQLite database and mocked Google/calendar."""
import sys
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from flask import redirect
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from models import db, User, ClientInstallation, FocusSession
from pig_shop import WEEKLY_ITEMS, SEASONAL_ITEMS, RARE_ITEMS, LEGACY_ITEMS

NOW=datetime(2026,10,5,12,tzinfo=timezone.utc)
CLIENT='7b72a384-e915-4b92-8d8e-15c25e8157f8'


def main():
    with tempfile.TemporaryDirectory(prefix='growing-shop-') as directory:
        app=create_app({'SQLALCHEMY_DATABASE_URI':'sqlite:///'+directory+'/test.db',
                        'SECRET_KEY':'shop-browser-only', 'GOOGLE_CLIENT_ID':'mock', 'GOOGLE_CLIENT_SECRET':'mock'})
        with app.app_context():
            db.create_all()
            user=User(google_sub='shop-browser'); db.session.add(user); db.session.flush()
            db.session.add(ClientInstallation(user_id=user.id,client_id=CLIENT))
            for i in range(10):
                db.session.add(FocusSession(client_id=CLIENT,task='A little daily focus',planned_minutes=480,
                    actual_minutes=480,focus_score=98,completed=True,
                    started_at=NOW-timedelta(days=i,minutes=480),ended_at=NOW-timedelta(days=i)))
            db.session.commit()
        server=make_server('127.0.0.1',0,app,threaded=True)
        base=f'http://127.0.0.1:{server.server_port}'; app.config['OAUTH_REDIRECT_URI']=base+'/auth/callback'
        threading.Thread(target=server.serve_forever,daemon=True).start()
        google=app.extensions['lock_oauth'].google
        try:
            with patch.object(google,'authorize_redirect',return_value=redirect('/auth/callback?code=mock')), patch.object(google,'authorize_access_token',return_value={'userinfo':{'sub':'shop-browser'}}), patch('pig_shop.datetime',wraps=datetime) as calendar, sync_playwright() as p:
                calendar.now.return_value=NOW
                browser=p.chromium.launch(); context=browser.new_context(viewport={'width':1280,'height':950})
                page=context.new_page(); errors=[]; failures=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('console',lambda message:errors.append(message.text) if message.type=='error' else None)
                page.on('response',lambda response:failures.append(response.url) if response.status>=500 else None)
                page.goto(base+'/login');page.get_by_role('link',name='Continue with Google').click()
                page.wait_for_function('document.getElementById("pig-coins").textContent === "4,800 focus coins"')
                page.get_by_role('button',name='Customize Pig Room').click()
                assert page.locator('.shop-section:visible').count()==5
                assert page.locator('[data-shop-section="weekly"] .pig-item-card:visible').count()==4
                page.locator('#shop-navigation').get_by_role('button',name='This Week’s Finds ✨').click()
                heading=page.locator('[data-shop-section="weekly"] > h3').bounding_box()
                sticky=page.locator('.customizer-header').bounding_box()
                assert heading['y'] >= sticky['y']+sticky['height']
                page.locator('#pig-customizer').screenshot(path='/tmp/lock-growing-shop-weekly.png')
                expected_spent=0
                def unlock_and_equip(definition):
                    nonlocal expected_spent
                    name=definition['name']
                    page.get_by_role('button',name='Unlock '+name,exact=True).click()
                    page.get_by_role('button',name='Equip '+name,exact=True).wait_for()
                    expected_spent+=definition['cost']
                    page.get_by_role('button',name='Equip '+name,exact=True).click()
                    page.get_by_role('button',name='Unequip '+name,exact=True).wait_for()
                    asset=definition['asset']
                    art=page.locator(f'[data-pig-item="{asset}"], [data-pig-base="{asset}"]')
                    assert art.get_attribute('data-style')==definition['style']
                    assert art.get_attribute('display')=='inline'
                    preview=page.locator(f'[data-item-card="{definition["id"]}"] .item-preview')
                    assert preview.locator('g').first.get_attribute('data-style')==definition['style']
                for definition in LEGACY_ITEMS:
                    if definition['cost']: unlock_and_equip(definition)
                # Buy the current weekly collection, then future finds when they rotate in.
                acquired=set()
                for week in range(6):
                    calendar.now.return_value=NOW+timedelta(weeks=week)
                    page.evaluate('load()'); page.wait_for_function('!loading')
                    snapshot=context.request.get(base+'/api/me/pig').json()['pig']
                    assert page.locator('[data-shop-section="weekly"] .pig-item-card:visible').count()==4
                    for definition in WEEKLY_ITEMS:
                        if definition['id'] in snapshot['shop']['weekly_ids'] and definition['id'] not in acquired:
                            unlock_and_equip(definition); acquired.add(definition['id'])
                    assert page.locator('.pig-item-card:visible').count()==sum(item['visible'] for item in context.request.get(base+'/api/me/pig').json()['pig']['items'])
                assert len(acquired)==6
                # Each seasonal find can be purchased only during its corresponding period.
                for definition, month in zip(SEASONAL_ITEMS,[10,12,2,3]):
                    calendar.now.return_value=NOW.replace(month=month)
                    page.evaluate('load()'); page.wait_for_function('!loading')
                    unlock_and_equip(definition)
                for definition in RARE_ITEMS: unlock_and_equip(definition)
                assert page.locator('#customizer-coins').inner_text()==f'{4800-expected_spent:,} coins to make it cozy'
                # Automatically earned milestones need no purchase.
                for name in ['Star Glasses','Cozy Blanket','Flower Vase','Little Victory Pennant','Cloud Rug']:
                    page.get_by_role('button',name='Equip '+name,exact=True).click()
                    page.get_by_role('button',name='Unequip '+name,exact=True).wait_for()
                # Preserve focused owned controls when their collection becomes Keepsakes.
                tulip=page.get_by_role('button',name='Unequip Tulip Plant',exact=True)
                tulip.focus(); calendar.now.return_value=NOW.replace(month=7)
                page.evaluate('load()'); page.wait_for_function('!loading')
                assert tulip.evaluate('el=>el===document.activeElement')
                assert page.locator('[data-item-card="plant_tulip"]').evaluate('el=>el.closest("[data-shop-section]").dataset.shopSection')=='keepsakes'
                page.keyboard.press('Escape')
                page.locator('.pig-panel').screenshot(path='/tmp/lock-growing-shop-room.png')
                calendar.now.return_value=NOW.replace(month=7)
                page.reload();page.wait_for_function('document.getElementById("pig-coins").textContent.includes("1,970")')
                page.get_by_role('button',name='Customize Pig Room').click()
                assert page.locator('[data-shop-section="keepsakes"] .pig-item-card:visible').count()>=4
                assert page.locator('[data-shop-section="seasonal"]').is_hidden()
                # Off-season ownership and style replacements survive the reload.
                for name in ['Ghost Mug','Hot Cocoa','Heart Rug','Tulip Plant']:
                    assert page.get_by_role('button',name='Equip '+name,exact=True).is_visible() or page.get_by_role('button',name='Unequip '+name,exact=True).is_visible()
                page.get_by_role('button',name='Equip Ghost Mug',exact=True).click()
                page.get_by_role('button',name='Unequip Ghost Mug',exact=True).wait_for()
                assert page.get_by_role('button',name='Equip Hot Cocoa',exact=True).is_visible()
                assert page.locator('[data-pig-item="mug"]').get_attribute('data-style')=='ghost'
                for width in [1280,768,390,320]:
                    page.set_viewport_size({'width':width,'height':950})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    assert page.locator('#pig-customizer').evaluate('el=>el.scrollWidth<=el.clientWidth')
                    page.locator('#pig-customizer').evaluate('el=>el.scrollTop=0')
                    page.locator('#pig-customizer').screenshot(path=f'/tmp/lock-growing-shop-{width}.png')
                    page.locator('#shop-navigation').get_by_role('button',name='Rare Treats',exact=True).click()
                    for _ in range(40):
                        page.keyboard.press('Tab')
                        assert page.evaluate('document.getElementById("pig-customizer").contains(document.activeElement)')
                page.emulate_media(reduced_motion='reduce')
                assert page.locator('.pig-item-card button').first.evaluate('el=>getComputedStyle(el).transitionDuration')=='0s'
                page.keyboard.press('Escape')
                assert page.locator('#customize-pig').evaluate('el=>el===document.activeElement')
                assert page.locator('#sessions tr').count()==10
                assert page.locator('#minutes').inner_text()=='4800.0 min'
                assert not errors,errors
                assert not failures,failures
                print('PASS: original inventory, grouped shop, six rotating variants across six weeks, all four seasons and off-season keepsakes, milestone equipment, rare purchases, slot replacement, exact unchanged coin economy, reload persistence, real room previews, auth/analytics, keyboard and 1280/768/390/320px; no console or HTTP 5xx errors')
                context.close();browser.close()
        finally:
            server.shutdown();server.server_close()
            with app.app_context():db.session.remove();db.engine.dispose()


if __name__=='__main__':main()
