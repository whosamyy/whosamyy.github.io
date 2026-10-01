# Requires Playwright and its Chromium browser. Port 5000 must be free.
# Temporary fixture pre-grants reddit.com; manually verify native permission prompts.
import os, sys, tempfile, json, shutil, threading
from pathlib import Path
project = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project / 'backend'))
from app import create_app
from models import db, FocusSession, BlockedAttempt
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
app=create_app({'SQLALCHEMY_DATABASE_URI':'sqlite:///'+tempfile.mktemp(suffix='.db')})
with app.app_context(): db.create_all()
server=make_server('127.0.0.1',5000,app,threaded=True)
threading.Thread(target=server.serve_forever,daemon=True).start()
fixture=Path(tempfile.mkdtemp(prefix='phase2-extension-'))
shutil.copytree(project / 'extension',fixture,dirs_exist_ok=True)
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
    popup.locator('#end').click();popup.locator('#summary').wait_for(state='visible');worker.evaluate('networkQueue')
    assert worker.evaluate('chrome.declarativeNetRequest.getDynamicRules()')==[]
    with app.app_context():
        s=db.session.get(FocusSession,session['backendSessionId']);assert s.ended_at and s.blocked_count==2 and s.focus_score == 50
        assert db.session.query(BlockedAttempt).count()==2
    dashboard=context.new_page();dashboard.goto(f'http://127.0.0.1:5000/?client_id={cid}')
    dashboard.wait_for_function('document.getElementById("blocked").textContent==="2"')
    assert dashboard.locator('#sessions tr').count()==1
    assert dashboard.locator('.bar').count()==1
    dashboard.screenshot(path='/tmp/phase2-dashboard.png',full_page=True)
    dashboard.goto('http://127.0.0.1:5000/?client_id=empty')
    dashboard.wait_for_function('document.getElementById("status").textContent.includes("No sessions yet")')
    for suffix in ['', '?client_id=invalid%2Fid']:
        dashboard.goto('http://127.0.0.1:5000/' + suffix)
        dashboard.wait_for_function('!document.getElementById("status").textContent.includes("Loading")')
        assert dashboard.locator('h1').inner_text() == 'LOCK IN BRO.'
    print('PASS online: real DNR redirects, popup closure, backend ID, attempt rows, finish, dashboard, chart, empty state')
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
