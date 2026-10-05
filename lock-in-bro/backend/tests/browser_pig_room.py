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
                assert page.locator('.pig-item-card:visible').count() == sum(item['visible'] for item in context.request.get(base+'/api/me/pig').json()['pig']['items'])
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
                assert page.locator('#customizer-coins').inner_text() == '825 coins to make it cozy'
                assert page.evaluate('document.body.dataset.weather === document.querySelector(".pig-art").dataset.weather && document.body.dataset.weather === "sparkle"')
                page.get_by_role('button', name='Equip Pink Mug', exact=True).click()
                page.get_by_role('button', name='Unequip Pink Mug', exact=True).wait_for()
                for name in ['Heart Lamp', 'Little Book Stack', 'Heart Poster', 'Fairy Lights', 'Desk Plant']:
                    page.get_by_role('button', name='Unlock '+name, exact=True).click()
                    page.get_by_role('button', name='Equip '+name, exact=True).wait_for()
                    page.get_by_role('button', name='Equip '+name, exact=True).click()
                    page.get_by_role('button', name='Unequip '+name, exact=True).wait_for()
                assert page.locator('#customizer-coins').inner_text() == '30 coins to make it cozy'
                page.locator('#pig-customizer').evaluate('el => el.scrollTop = 0')
                page.locator('#pig-customizer').screenshot(path='/tmp/lock-pig-world-customizer.png')
                page.keyboard.press('Escape')
                assert page.locator('#customize-pig').evaluate('el => el === document.activeElement')
                page.reload(); page.wait_for_function('document.getElementById("pig-coins").textContent === "30 focus coins"')
                assert page.locator('[data-pig-item][display="inline"]').count() == 12
                for mood in ['happy', 'proud', 'cozy', 'sleepy', 'distracted', 'excited']:
                    page.evaluate('(mood) => {celebrationUntil = 0; renderPig({...pigState, mood});}', mood)
                    if mood == 'cozy':
                        assert page.locator('.pig-eyes-open').first.evaluate('el => getComputedStyle(el).display') != 'none'
                    else:
                        assert page.locator('.pig-eyes-open').first.evaluate('el => getComputedStyle(el).display') == 'none'
                        assert page.locator(f'.pig-mood-face[data-mood="{mood}"]').first.evaluate('el => getComputedStyle(el).display') != 'none'
                # Real account data, with only the weather field varied for visual QA.
                # Polls reuse the same fixture so long screenshot runs stay deterministic.
                visual_stats = context.request.get(base+'/api/me/stats').json()
                def visual_weather(route):
                    route.fulfill(json=visual_stats)
                page.route('**/api/me/stats*', visual_weather)
                gradients = set()
                for weather in ['sunny', 'cloudy', 'rainy', 'night', 'sparkle']:
                    visual_stats['pig']['weather'] = weather
                    page.evaluate('(weather) => renderPig({...pigState, weather})', weather)
                    assert page.evaluate('document.body.dataset.weather === document.querySelector(".pig-art").dataset.weather')
                    assert page.locator(f'.weather-state[data-weather="{weather}"]').evaluate('el => getComputedStyle(el).display') != 'none'
                    plane = page.locator('.weather-plane-'+weather)
                    page.wait_for_function('(state) => Number(getComputedStyle(document.querySelector(".weather-plane-"+state)).opacity) > .99', arg=weather)
                    gradients.add(plane.evaluate('el => getComputedStyle(el).backgroundImage'))
                    assert page.locator('.weather-background').get_attribute('aria-hidden') == 'true'
                    assert page.locator('.weather-background').evaluate('el => getComputedStyle(el).position') == 'fixed'
                    assert page.locator('.weather-background').evaluate('el => [el, ...el.querySelectorAll("*")].every(node => getComputedStyle(node).pointerEvents === "none")')
                    # Verify readable text against every opaque color in the active gradient.
                    assert page.evaluate(r"""() => {
                        const rgb = value => value.match(/[\d.]+/g).slice(0,3).map(Number);
                        const luminance = color => color.map(c => c/255).map(c => c <= .04045 ? c/12.92 : ((c+.055)/1.055)**2.4).reduce((sum,c,i)=>sum+c*[.2126,.7152,.0722][i],0);
                        const contrast = (a,b) => (Math.max(luminance(a),luminance(b))+.05)/(Math.min(luminance(a),luminance(b))+.05);
                        const plane = document.querySelector('.weather-plane-'+document.body.dataset.weather);
                        const colors = [...getComputedStyle(plane).backgroundImage.matchAll(/rgba?\(([^)]+)\)/g)].map(m=>m[1].split(',').map(Number)).filter(c=>c.length===3 || c[3]===1);
                        const header = rgb(getComputedStyle(document.querySelector('main > header')).color);
                        const privacy = rgb(getComputedStyle(document.querySelector('main > .privacy')).color);
                        return colors.every(color=>contrast(header,color)>=4.5 && contrast(privacy,color)>=4.5) &&
                            [...document.querySelectorAll('.cards article, .panel:not(.pig-panel)')].every(card=>contrast(rgb(getComputedStyle(card).color),rgb(getComputedStyle(card).backgroundColor))>=4.5);
                    }"""), weather
                    for width in [1280, 768, 390, 320]:
                        page.set_viewport_size({'width': width, 'height': 1000})
                        page.evaluate('scrollTo(0, 0)')
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        page.screenshot(path=f'/tmp/lock-global-weather-{weather}-{width}.png')
                        # Decorations cannot intercept the room customization button.
                        page.get_by_role('button', name='Customize Pig Room').click()
                        assert page.locator('#pig-customizer').evaluate('el => el.open')
                        page.keyboard.press('Escape')
                        page.locator('#sessions').scroll_into_view_if_needed()
                        assert page.locator('.weather-background').bounding_box()['y'] == 0
                        assert page.locator('#sessions tr').count() == 3
                    page.locator('.pig-panel').screenshot(path=f'/tmp/lock-pig-world-{weather}.png')
                assert len(gradients) == 5
                # Reduced motion leaves all five static atmospheres visible on selection.
                page.emulate_media(reduced_motion='reduce')
                for weather in ['sunny', 'cloudy', 'rainy', 'night', 'sparkle']:
                    visual_stats['pig']['weather'] = weather
                    page.evaluate('(weather) => renderPig({...pigState, weather})', weather)
                    assert page.locator('.weather-background').evaluate('el => [...el.querySelectorAll("*")].every(node => getComputedStyle(node).animationName === "none" && getComputedStyle(node).transitionDuration === "0s")')
                    assert page.locator('.weather-plane-'+weather).evaluate('el => getComputedStyle(el).opacity') == '1'
                page.emulate_media(reduced_motion='no-preference')
                page.unroute('**/api/me/stats*', visual_weather)
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
                print('PASS: mocked Google sign-in, real authenticated room APIs, all 12 items, coins, purchase/equip/reload persistence, all visual states and matching global weather/celebrations, five distinct gradients, readable contrast, click-through fixed backgrounds, live analytics, keyboard dialog/focus, 1280/768/390/320px, reduced motion; no console errors or HTTP 5xx')
                context.close(); browser.close()
        finally:
            server.shutdown(); server.server_close()
            with app.app_context():
                db.session.remove(); db.engine.dispose()


if __name__ == '__main__': main()
