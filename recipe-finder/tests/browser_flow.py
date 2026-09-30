"""Run with Python + playwright installed and Chrome available; uses real SQLite/API.
Recommendation provider alone is stubbed for deterministic, offline regression checks.
BACKEND_DIR may override the default sibling backend checkout. Ports 5001/8000 must be free.
"""
import functools
import os
from pathlib import Path
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import Mock, patch
from playwright.sync_api import sync_playwright, expect
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, os.environ.get('BACKEND_DIR', str(ROOT.parent / 'recipe-finder-backend')))


def main():
    with tempfile.TemporaryDirectory() as directory:
        os.environ['DATABASE_PATH'] = str(Path(directory) / 'browser.sqlite3')
        from app import app
        from test_app import RECIPE
        provider = Mock(status_code=200)
        provider.json.return_value = {'recipes': [RECIPE, {**RECIPE, 'id': 2, 'name': 'Second chicken', 'rating': 4.9}]}
        api = make_server('127.0.0.1', 5001, app, threaded=True)
        static = ThreadingHTTPServer(('127.0.0.1', 8000), functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
        for server in (api, static):
            threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with patch('app.requests.get', return_value=provider), sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                context = browser.new_context(viewport={'width': 1280, 'height': 900})
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto('http://localhost:8000/recipe-finder/')
                expect(page.locator('#saved-grid')).to_contain_text('No saved recipes yet')
                page.locator('#find-recipes').click()
                expect(page.locator('#input-message')).to_contain_text('Add at least one ingredient')
                page.locator('#ingredient-input').fill('chicken, rice')
                page.locator('#find-recipes').click()
                expect(page.locator('#recipe-grid .recipe-card')).to_have_count(2)
                page.locator('#recipe-grid [data-favorite="1"]').click()
                expect(page.locator('#saved-grid .recipe-card')).to_have_count(1)
                expect(page.locator('#recipe-grid [data-favorite="1"]')).to_have_text('♥ Unsave')
                page.locator('#favorites-only').check()
                expect(page.locator('#recipe-grid .recipe-card')).to_have_count(1)
                page.locator('#recipe-grid [data-details]').click()
                expect(page.locator('#recipe-modal')).to_be_visible()
                page.locator('#close-modal').click()
                page.locator('#surprise-me').click()
                expect(page.locator('#recipe-modal')).to_be_visible()
                page.locator('#close-modal').click()
                page.locator('#favorites-only').uncheck()
                page.locator('#sort').select_option('rating')
                expect(page.locator('#recipe-grid h3').first).to_have_text('Second chicken')
                page.locator('#max-time').select_option('30')
                expect(page.locator('#recipe-grid .recipe-card')).to_have_count(2)
                page.reload()
                expect(page.locator('#saved-grid .recipe-card')).to_have_count(1)
                keys = page.evaluate('Object.keys(localStorage)')
                assert keys == ['recipe-finder-client-id'], keys
                other = browser.new_context()
                other_page = other.new_page()
                other_page.goto('http://localhost:8000/recipe-finder/')
                expect(other_page.locator('#saved-grid')).to_contain_text('No saved recipes yet')
                other.close()
                page.set_viewport_size({'width': 390, 'height': 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.screenshot(path='/tmp/recipe-saved-mobile.png', full_page=True)
                page.locator('#saved-grid [data-favorite]').click()
                expect(page.locator('#saved-grid')).to_contain_text('No saved recipes yet')
                page.reload()
                expect(page.locator('#saved-grid')).to_contain_text('No saved recipes yet')
                page.route('**/favorites?*', lambda route: route.abort())
                page.locator('#refresh-saved').click()
                expect(page.locator('#saved-status')).to_contain_text("Couldn't reach saved recipes")
                page.unroute('**/favorites?*')
                page.locator('#refresh-saved').click()
                expect(page.locator('#saved-status')).to_have_text('')
                page.locator('#ingredient-input').fill('rice')
                page.locator('#find-recipes').click()
                expect(page.locator('#recipe-grid .recipe-card')).to_have_count(2)
                page.route('**/favorites', lambda route: route.fulfill(status=503, content_type='application/json', body='{"success":false,"error":"Saved recipes unavailable"}'))
                page.locator('#recipe-grid [data-favorite="1"]').click()
                expect(page.locator('#saved-status')).to_contain_text('Saved recipes unavailable')
                expect(page.locator('#recipe-grid [data-favorite="1"]')).to_have_text('♡ Save')
                page.unroute('**/favorites')
                page.locator('#recipe-grid [data-favorite="1"]').click()
                expect(page.locator('#saved-grid .recipe-card')).to_have_count(1)
                page.route('**/favorites/1?*', lambda route: route.abort())
                page.locator('#saved-grid [data-favorite]').click()
                expect(page.locator('#saved-status')).to_contain_text("Couldn't reach saved recipes")
                expect(page.locator('#saved-grid .recipe-card')).to_have_count(1)
                assert not errors, errors
                browser.close()
                print('PASS: search, save, reload, isolation, unsave, filters, sort, details, Surprise Me, mobile layout, API failures/retry, localStorage ID-only, no JS exceptions')
        finally:
            api.shutdown()
            static.shutdown()


if __name__ == '__main__':
    main()
