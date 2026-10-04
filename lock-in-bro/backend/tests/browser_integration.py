# Requires Playwright and its Chromium browser. Port 5000 must be free.
# Temporary fixture pre-grants reddit.com; manually verify native permission prompts.
import os, sys, tempfile, json, shutil, threading
from unittest.mock import patch
from pathlib import Path
project = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project / 'backend'))
from app import create_app
from models import db, FocusSession, BlockedAttempt
from flask import redirect
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
app=create_app({'SQLALCHEMY_DATABASE_URI':'sqlite:///'+tempfile.mktemp(suffix='.db'),
    'SECRET_KEY':'browser-test-only-key', 'GOOGLE_CLIENT_ID':'browser-test-client',
    'GOOGLE_CLIENT_SECRET':'browser-test-secret'})
# Only test fixtures stub Google. The extension still writes anonymously.
google=app.extensions['lock_oauth'].google
oauth_start=patch.object(google,'authorize_redirect',return_value=redirect('/auth/callback?code=mock'))
oauth_token=patch.object(google,'authorize_access_token',return_value={'userinfo':{'sub':'browser-test-google-sub'}})
oauth_start.start();oauth_token.start()
with app.app_context(): db.create_all()
server=make_server('127.0.0.1',5000,app,threaded=True)
threading.Thread(target=server.serve_forever,daemon=True).start()
fixture=Path(tempfile.mkdtemp(prefix='phase2-extension-'))
shutil.copytree(project / 'extension',fixture,dirs_exist_ok=True)
# Keep integration traffic in the temporary local database, even for production builds.
(fixture/'config.js').write_text("const BACKEND = 'http://127.0.0.1:5000';\n")
manifest=json.loads((fixture/'manifest.json').read_text())
manifest['host_permissions'] += ['http://*.reddit.com/*','https://*.reddit.com/*']
(fixture/'manifest.json').write_text(json.dumps(manifest))
with sync_playwright() as p:
    context=p.chromium.launch_persistent_context(tempfile.mkdtemp(),channel='chromium',headless=True,args=[f'--disable-extensions-except={fixture}',f'--load-extension={fixture}'])
    errors=[]
    context.on('weberror',lambda e: errors.append(str(e)))
    worker=context.service_workers[0] if context.service_workers else context.wait_for_event('serviceworker')
    eid=worker.url.split('/')[2]
    popup=context.new_page();popup.goto(f'chrome-extension://{eid}/popup.html')
    popup.locator('#domain').fill('reddit.com');popup.locator('#add-form button').click()
    popup.wait_for_function('document.getElementById("sites").textContent.includes("reddit.com")')
    popup.locator('#task').fill('Phase 2 browser test');popup.locator('#start').click()
    popup.locator('#active').wait_for(state='visible')
    worker.evaluate('networkQueue')
    session=worker.evaluate('chrome.storage.local.get("session")')['session']
    assert session['backendSessionId']
    cid=worker.evaluate('chrome.storage.local.get("client_id")')['client_id']
    popup.close()
    for url in ['https://reddit.com','http://www.reddit.com']:
        tab=context.new_page();tab.goto(url);assert '/blocked.html?' in tab.url
        tab.wait_for_function('document.getElementById("task").textContent.includes("Phase 2")')
        worker.evaluate('queue');worker.evaluate('networkQueue');tab.close()
    assert worker.evaluate('chrome.storage.local.get("session")')['session']['blockedCount']==2
    popup=context.new_page();popup.goto(f'chrome-extension://{eid}/popup.html')
    dashboard=context.new_page();dashboard.goto(f'http://127.0.0.1:5000/?client_id={cid}')
    assert dashboard.url.endswith('/login')
    dashboard.screenshot(path='/tmp/lock-auth-login.png',full_page=True)
    dashboard.set_viewport_size({'width':390,'height':844})
    assert dashboard.get_by_role('link',name='Continue with Google').is_visible()
    dashboard.screenshot(path='/tmp/lock-auth-login-mobile.png',full_page=True)
    dashboard.set_viewport_size({'width':1280,'height':900})
    dashboard.get_by_role('link',name='Continue with Google').click()
    dashboard.wait_for_function('document.getElementById("sessions").textContent.includes("In progress")')
    assert dashboard.url == 'http://127.0.0.1:5000/'
    popup.locator('#end').click();popup.locator('#summary').wait_for(state='visible');worker.evaluate('networkQueue')
    # The already-open dashboard must reflect completion without a reload.
    dashboard.wait_for_function('document.getElementById("sessions").textContent.includes("Ended early")')
    assert worker.evaluate('chrome.declarativeNetRequest.getDynamicRules()')==[]
    with app.app_context():
        s=db.session.get(FocusSession,session['backendSessionId']);assert s.ended_at and s.blocked_count==2 and s.focus_score == 50
        assert db.session.query(BlockedAttempt).count()==2
    dashboard.wait_for_function('document.getElementById("blocked").textContent==="2"')
    assert dashboard.locator('#sessions tr').count()==1
    assert dashboard.locator('.bar').count()==1
    assert dashboard.locator('#pig-level').inner_text()=='Level 1'
    assert dashboard.locator('#pig-progress').get_attribute('value')=='0'
    dashboard.screenshot(path='/tmp/phase2-dashboard.png',full_page=True)
    # Completed sessions update the same open dashboard; early finishes earned no XP.
    for index, minutes in enumerate([40, 40, 80]):
        response=dashboard.request.post('http://127.0.0.1:5000/api/sessions',data={
            'client_id':cid,'task':'Pig reward test','planned_minutes':minutes,
            'blocked_domains':['reddit.com'],'started_at':f'2026-10-04T10:0{index}:00Z'})
        sid=response.json()['session_id']
        assert dashboard.request.post(f'http://127.0.0.1:5000/api/sessions/{sid}/finish',data={
            'ended_at':'2026-10-04T12:00:00Z','completed':True,'actual_minutes':minutes,
            'blocked_count':0,'focus_score':100}).ok
    dashboard.wait_for_function('document.getElementById("pig-level").textContent==="Level 3"')
    assert dashboard.locator('#pig-xp').inner_text()=='XP: 20 / 100'
    assert dashboard.locator('#pig-unlocks li').count()==2
    assert dashboard.locator('[data-pig-item="bow"]').get_attribute('display')=='inline'
    assert dashboard.locator('#sessions tr').count()==4
    dashboard.locator('.pig-panel').screenshot(path='/tmp/lock-pig-desktop.png')
    dashboard.set_viewport_size({'width':390,'height':844})
    dashboard.locator('.pig-panel').screenshot(path='/tmp/lock-pig-mobile.png')
    assert dashboard.evaluate('document.documentElement.scrollWidth <= innerWidth')
    dashboard.reload()
    dashboard.wait_for_function('document.getElementById("pig-level").textContent==="Level 3"')
    assert dashboard.locator('#pig-unlocks li').count()==2
    dashboard.emulate_media(reduced_motion='reduce')
    assert dashboard.locator('.pig-float').evaluate('el=>getComputedStyle(el).animationName')=='none'
    for index, minutes in enumerate([480, 160], start=3):
        response=dashboard.request.post('http://127.0.0.1:5000/api/sessions',data={
            'client_id':cid,'task':'More pig rewards','planned_minutes':minutes,
            'blocked_domains':['reddit.com'],'started_at':f'2026-10-04T10:0{index}:00Z'})
        sid=response.json()['session_id']
        assert dashboard.request.post(f'http://127.0.0.1:5000/api/sessions/{sid}/finish',data={
            'ended_at':'2026-10-04T23:00:00Z','completed':True,'actual_minutes':minutes,
            'blocked_count':0,'focus_score':100}).ok
    dashboard.wait_for_function('document.getElementById("pig-level").textContent==="Level 10"')
    assert dashboard.locator('#pig-unlocks li').count()==5
    assert dashboard.locator('[data-pig-item][display="inline"]').count()==5
    dashboard.locator('.pig-panel').screenshot(path='/tmp/lock-pig-all-goodies.png')
    dashboard.get_by_role('button',name='Sign out').click()
    assert dashboard.url.endswith('/login')
    assert dashboard.request.get('http://127.0.0.1:5000/api/me/stats').status==401
    dashboard.goto('http://127.0.0.1:5000/?client_id=invalid%2Fid')
    assert dashboard.get_by_role('alert').is_visible()
    assert dashboard.locator('h1').inner_text() == 'LOCK IN BRO.'
    print('PASS online: anonymous writes, real DNR redirects, popup closure, backend ID, attempt rows, mocked Google login, clean dashboard URL, live analytics/pig refresh, all accessories, persistent XP, responsive layout, reduced motion, logout, invalid link')
    server.shutdown();server.server_close()
    popup.locator('#task').fill('Phase 2 offline test')
    popup.locator('#start').click();popup.locator('#active').wait_for(state='visible')
    tab=context.new_page();tab.goto('https://reddit.com');assert '/blocked.html?' in tab.url
    tab.wait_for_function('document.getElementById("task").textContent.includes("Phase 2")')
    popup.locator('#end').click();popup.locator('#summary').wait_for(state='visible');worker.evaluate('networkQueue')
    assert worker.evaluate('chrome.storage.local.get("summary")')['summary']['blockedCount']==1
    assert worker.evaluate('chrome.storage.local.get("client_id")')['client_id']==cid
    popup.locator('#start').click();popup.locator('#active').wait_for(state='visible')
    worker.evaluate('async()=>{const {session}=await chrome.storage.local.get("session");session.plannedEnd=Date.now()-1;await chrome.storage.local.set({session});await serial(reconcile);}')
    assert worker.evaluate('chrome.storage.local.get("summary")')['summary']['completed']
    assert worker.evaluate('chrome.declarativeNetRequest.getDynamicRules()')==[]
    assert not errors,errors
    print('PASS offline: start, redirect, count, manual finish, automatic expiry, stable client ID; no uncaught browser errors')
    context.close()
oauth_start.stop();oauth_token.stop()
