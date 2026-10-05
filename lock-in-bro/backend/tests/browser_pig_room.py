"""Local browser QA. Uses a temporary SQLite DB and mocked Google provider only.

Run with the existing Playwright environment and browser installation. Never uses
production credentials/data. Screenshots go to /tmp/lock-pig-world-*.png.
"""
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


def main():
    with tempfile.TemporaryDirectory(prefix='pig-world-qa-') as directory:
        app = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///'+directory+'/test.db',
                          'SECRET_KEY': 'browser-room-test', 'GOOGLE_CLIENT_ID': 'mock',
                          'GOOGLE_CLIENT_SECRET': 'mock'})
        with app.app_context():
            db.create_all()
            user = User(google_sub='room-browser-test'); db.session.add(user); db.session.flush()
            db.session.add(ClientInstallation(user_id=user.id, client_id='7b72a384-e915-4b92-8d8e-15c25e8157f8'))
            now = datetime.now(timezone.utc)
            for i, minutes in enumerate([300, 400, 200]):
                db.session.add(FocusSession(client_id='7b72a384-e915-4b92-8d8e-15c25e8157f8', task='Cozy study '+str(i),
                    planned_minutes=minutes, actual_minutes=minutes, completed=True, focus_score=95,
                    started_at=now-timedelta(hours=i+1), ended_at=now-timedelta(minutes=i)))
            db.session.commit()
        server = make_server('127.0.0.1', 0, app, threaded=True)
        app.config['OAUTH_REDIRECT_URI'] = f'http://127.0.0.1:{server.server_port}/auth/callback'
        base = f'http://127.0.0.1:{server.server_port}'
        threading.Thread(target=server.serve_forever, daemon=True).start()
        google = app.extensions['lock_oauth'].google
        try:
            with patch.object(google, 'authorize_redirect', return_value=redirect('/auth/callback?code=mock')), patch.object(google, 'authorize_access_token', return_value={'userinfo': {'sub': 'room-browser-test'}}), sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context(viewport={'width': 1280, 'height': 1000}, timezone_id='America/New_York')
                page = context.new_page()
                errors = []; failures = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
                page.on('response', lambda response: failures.append(response.url) if response.status >= 500 else None)
                page.goto(base+'/login'); page.get_by_role('link', name='Continue with Google').click()
                page.wait_for_function('document.getElementById("pig-level").textContent === "Level 10"')
                assert page.locator('#minutes').inner_text() == '900.0 min'
                assert page.locator('#sessions tr').count() == 3
                assert page.locator('.bar').count() >= 1
                assert page.locator('#pig-coins').inner_text() == '900 focus coins'
                page.get_by_role('button', name='Customize Pig Room').click()
                assert page.locator('#pig-customizer').evaluate('el => el.open')
                assert page.locator('.pig-item-card').count() == 12
                # A refresh preserves focused controls in the open panel.
                # Existing accessories default to equipped, so focus the Unequip control.
                button = page.get_by_role('button', name='Unequip Pink Bow', exact=True)
                button.focus(); page.evaluate('load()')
                page.wait_for_function('!loading')
                assert button.evaluate('el => el === document.activeElement')
                # Hold a pre-purchase stats snapshot, then release it after mutation.
                # It must not overwrite the newer coin/equipment state.
                held = []
                def hold_stats(route):
                    response = route.fetch()
                    held.append((route, response))
                page.route('**/api/me/stats*', hold_stats)
                page.evaluate('() => { load(); }')
                page.wait_for_timeout(100)
                assert held
                page.get_by_role('button', name='Unlock Pink Mug', exact=True).click()
                page.get_by_role('button', name='Equip Pink Mug', exact=True).wait_for()
                page.unroute('**/api/me/stats*', hold_stats)
                for route, response in held:
                    route.fulfill(response=response)
                page.wait_for_function('!loading')
                assert page.locator('#customizer-coins').inner_text() == '875 coins to make it cozy'
                page.get_by_role('button', name='Equip Pink Mug', exact=True).click()
                page.get_by_role('button', name='Unequip Pink Mug', exact=True).wait_for()
                for name in ['Heart Lamp', 'Little Book Stack', 'Heart Poster', 'Fairy Lights', 'Desk Plant']:
                    page.get_by_role('button', name='Unlock '+name, exact=True).click()
                    page.get_by_role('button', name='Equip '+name, exact=True).wait_for()
                    page.get_by_role('button', name='Equip '+name, exact=True).click()
                    page.get_by_role('button', name='Unequip '+name, exact=True).wait_for()
                assert page.locator('#customizer-coins').inner_text() == '610 coins to make it cozy'
                page.locator('#pig-customizer').evaluate('el => el.scrollTop = 0')
                page.locator('#pig-customizer').screenshot(path='/tmp/lock-pig-world-customizer.png')
                page.keyboard.press('Escape')
                assert page.locator('#customize-pig').evaluate('el => el === document.activeElement')
                page.reload(); page.wait_for_function('document.getElementById("pig-coins").textContent === "610 focus coins"')
                assert page.locator('[data-pig-item][display="inline"]').count() == 12
                for mood in ['happy', 'proud', 'cozy', 'sleepy', 'distracted', 'excited']:
                    page.evaluate('(mood) => {celebrationUntil = 0; renderPig({...pigState, mood});}', mood)
                    if mood == 'cozy':
                        assert page.locator('.pig-eyes-open').first.evaluate('el => getComputedStyle(el).display') != 'none'
                    else:
                        assert page.locator('.pig-eyes-open').first.evaluate('el => getComputedStyle(el).display') == 'none'
                        assert page.locator(f'.pig-mood-face[data-mood="{mood}"]').first.evaluate('el => getComputedStyle(el).display') != 'none'
                for weather in ['sunny', 'cloudy', 'rainy', 'night', 'sparkle']:
                    page.evaluate('(weather) => renderPig({...pigState, weather})', weather)
                    assert page.locator(f'.weather-state[data-weather="{weather}"]').evaluate('el => getComputedStyle(el).display') != 'none'
                    page.locator('.pig-panel').screenshot(path=f'/tmp/lock-pig-world-{weather}.png')
                for width in [1280, 768, 390, 320]:
                    page.set_viewport_size({'width': width, 'height': 1000})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.locator('.pig-panel').screenshot(path=f'/tmp/lock-pig-world-{width}.png')
                    page.get_by_role('button', name='Customize Pig Room').click()
                    assert page.locator('#pig-customizer').evaluate('el => el.scrollWidth <= el.clientWidth')
                    page.locator('#pig-customizer').screenshot(path=f'/tmp/lock-pig-world-customizer-{width}.png')
                    # Native modal keeps keyboard focus inside, including at 320px.
                    for _ in range(16):
                        page.keyboard.press('Tab')
                        assert page.evaluate('document.getElementById("pig-customizer").contains(document.activeElement)')
                    page.keyboard.press('Escape')
                page.emulate_media(reduced_motion='reduce')
                for selector in ['.pig-float', '.room-cloud', '.room-rain', '.room-sparkle', '.mug-steam']:
                    assert page.locator(selector).first.evaluate('el => getComputedStyle(el).animationName') == 'none'
                assert not errors, errors
                assert not failures, failures
                print('PASS: mocked Google sign-in, real authenticated room APIs, all 12 items, coins, purchase/equip/reload persistence, all visual states, live analytics, keyboard dialog/focus, 1280/768/390/320px, reduced motion; no console errors or HTTP 5xx')
                context.close(); browser.close()
        finally:
            server.shutdown(); server.server_close()
            with app.app_context():
                db.session.remove(); db.engine.dispose()


if __name__ == '__main__': main()
