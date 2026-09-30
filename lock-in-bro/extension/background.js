importScripts('focus-score.js');
// All state changes run in one queue, so simultaneous tabs cannot lose counts.
let queue = Promise.resolve();
function serial(work) {
  const result = queue.then(work);
  queue = result.catch(console.error);
  return result;
}
// Network work is ordered separately: no fetch can stall the local state queue.
const BACKEND = 'http://127.0.0.1:5000';
let networkQueue = Promise.resolve();
const backendIds = new Map();
async function clientId() {
  const stored = await chrome.storage.local.get('client_id');
  if (stored.client_id) return stored.client_id;
  const id = crypto.randomUUID();
  await chrome.storage.local.set({client_id: id});
  return id;
}
async function post(path, data) {
  const response = await fetch(`${BACKEND}${path}`, {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data), signal: AbortSignal.timeout(4000)
  });
  if (!response.ok) throw Error(`Backend returned ${response.status}`);
  return response.json();
}
function sync(work) {
  networkQueue = networkQueue.then(work).catch(error => {
    console.warn('[Lock In Bro] History sync unavailable; local blocking and recap remain available.', error.message);
  });
}
function syncStart(session, id) {
  sync(async () => {
    const result = await post('/api/sessions', {
      client_id: id, task: session.task, planned_minutes: session.plannedMinutes,
      blocked_domains: session.blocklist, started_at: new Date(session.startedAt).toISOString()
    });
    if (!Number.isInteger(result.session_id)) throw Error('Invalid backend session ID');
    backendIds.set(session.id, result.session_id);
    await serial(async () => {
      const state = await chrome.storage.local.get(['session', 'summary']);
      for (const key of ['session', 'summary']) {
        if (state[key]?.id === session.id) {
          state[key].backendSessionId = result.session_id;
          await chrome.storage.local.set({[key]: state[key]});
        }
      }
    });
  });
}
function syncAttempt(session, domain, timestamp) {
  sync(async () => {
    const id = session.backendSessionId || backendIds.get(session.id);
    if (id) await post(`/api/sessions/${id}/blocked`, {domain, timestamp});
  });
}
function syncFinish(summary) {
  sync(async () => {
    const id = summary.backendSessionId || backendIds.get(summary.id);
    try {
      if (id) await post(`/api/sessions/${id}/finish`, {
        ended_at: new Date(summary.endedAt).toISOString(), completed: summary.completed,
        actual_minutes: summary.actualMinutes, blocked_count: summary.blockedCount,
        focus_score: summary.focusScore
      });
    } finally { backendIds.delete(summary.id); }
  });
}
// Temporary development diagnostics: chosen domains and rules only, never browsing history.
const DEBUG_BLOCKING = true;
function debugBlockingLog(label, value) {
  if (DEBUG_BLOCKING) console.info(`[Lock In Bro] ${label}`, value);
}
function hostPatterns(domains) {
  // Chrome's *.example.com match pattern includes example.com itself.
  return domains.flatMap(domain => [`http://*.${domain}/*`, `https://*.${domain}/*`]);
}
function blockingRules(session) {
  return session.blocklist.map((domain, index) => ({
    id: index + 1,
    priority: 1,
    action: {
      type: 'redirect',
      redirect: {extensionPath: `/blocked.html?domain=${encodeURIComponent(domain)}&session=${session.id}`}
    },
    condition: {requestDomains: [domain], resourceTypes: ['main_frame']}
  }));
}
function rulesMatch(installed, expected) {
  // Compare relevant fields explicitly; Chrome need not preserve object-key order.
  return installed.length === expected.length && expected.every(rule => {
    const actual = installed.find(item => item.id === rule.id);
    return actual?.priority === rule.priority && actual.action.type === 'redirect' &&
      actual.action.redirect.extensionPath === rule.action.redirect.extensionPath &&
      Object.keys(actual.condition).length === 2 &&
      JSON.stringify(actual.condition.requestDomains) === JSON.stringify(rule.condition.requestDomains) &&
      JSON.stringify(actual.condition.resourceTypes) === JSON.stringify(rule.condition.resourceTypes);
  });
}
async function ensureBlocking(session, force = false) {
  try {
    const origins = hostPatterns(session.blocklist);
    const granted = await chrome.permissions.contains({origins});
    const expected = blockingRules(session);
    const installed = await chrome.declarativeNetRequest.getDynamicRules();
    if (force || !granted || !rulesMatch(installed, expected)) {
      debugBlockingLog('Normalized blocklist', session.blocklist);
      debugBlockingLog('Host permission check', {origins, granted});
      if (!granted) throw Error('Website access is missing. End the session and start again, allowing access to the selected sites.');
      debugBlockingLog('Generated DNR rules', expected);
      // Replace atomically so old IDs cannot collide with the new rules.
      await chrome.declarativeNetRequest.updateDynamicRules({
        removeRuleIds: installed.map(rule => rule.id), addRules: expected
      });
      debugBlockingLog('updateDynamicRules succeeded', true);
      const verified = await chrome.declarativeNetRequest.getDynamicRules();
      debugBlockingLog('Installed DNR rules', verified);
      if (!rulesMatch(verified, expected)) throw Error('Chrome did not retain the expected blocking rules.');
    }
  } catch (error) {
    // Promise-based Chrome APIs reject on failure; runtime.lastError is for callbacks.
    console.error('[Lock In Bro] Blocking setup failed:', error);
    throw error;
  }
}
// Run await debugBlocking() in the extension service worker console.
async function debugBlocking() {
  try {
    const {session} = await chrome.storage.local.get('session');
    const origins = hostPatterns(session?.blocklist || []);
    const result = {
      active: !!session?.active,
      blocklist: session?.blocklist || [],
      origins,
      hostPermissionGranted: origins.length > 0 && await chrome.permissions.contains({origins}),
      rules: await chrome.declarativeNetRequest.getDynamicRules()
    };
    console.info('[Lock In Bro] Blocking diagnostics', result);
    return result;
  } catch (error) {
    console.error('[Lock In Bro] Diagnostics failed:', error);
    throw error;
  }
}
async function clearRules() {
  try {
    const rules = await chrome.declarativeNetRequest.getDynamicRules();
    if (rules.length) {
      await chrome.declarativeNetRequest.updateDynamicRules({removeRuleIds: rules.map(r => r.id)});
      debugBlockingLog('Blocking rules cleared', true);
    }
  } catch (error) {
    console.error('[Lock In Bro] Clearing rules failed:', error);
    throw error;
  }
}
async function finish(completed) {
  await clearRules();
  await chrome.alarms.clear('focus-end');
  const {session} = await chrome.storage.local.get('session');
  if (!session?.active) return;
  const endedAt = completed ? session.plannedEnd : Date.now();
  const summary = {...session, active: false, endedAt, completed};
  summary.actualMinutes = Math.max(0, Math.min(session.plannedMinutes, (endedAt - session.startedAt) / 60000));
  summary.focusScore = null;
  try {
    const score = computeFocusScore({completed, plannedMinutes: session.plannedMinutes,
      actualMinutes: summary.actualMinutes, blockedCount: session.blockedCount});
    if (typeof score === 'number' && Number.isFinite(score) && score >= 0 && score <= 100) summary.focusScore = score;
  } catch (error) { console.warn('[Lock In Bro] Score unavailable:', error.message); }
  delete summary.countedDocuments;
  await chrome.storage.local.set({session: null, summary});
  syncFinish(summary);
}
async function reconcile() {
  const {session} = await chrome.storage.local.get('session');
  if (session?.active && Date.now() >= session.plannedEnd) await finish(true);
  else if (session?.active) {
    // Reload/startup can leave stored state without rules. Restore blocking too.
    try { await ensureBlocking(session); }
    catch (error) { await finish(false); throw error; }
    await chrome.alarms.create('focus-end', {when: session.plannedEnd});
  }
  else await clearRules();
}
function validDomain(domain) {
  return typeof domain === 'string' && domain.length <= 253 &&
    /^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/.test(domain);
}
async function handle(message, sender) {
  await reconcile();
  const state = await chrome.storage.local.get(['session', 'summary', 'blocklist']);
  const anonymousId = await clientId();
  if (message.type === 'state') return {...state, client_id: anonymousId};
  // Only our popup may change configuration or start/end sessions.
  const isPopup = sender.url === chrome.runtime.getURL('popup.html');
  if (message.type === 'save' && isPopup) {
    if (state.session?.active) throw Error('End the current session before changing sites.');
    if (!Array.isArray(message.domains) || message.domains.length > 100 || !message.domains.every(validDomain)) throw Error('Enter valid domains (maximum 100).');
    await chrome.storage.local.set({blocklist: [...new Set(message.domains)]});
  } else if (message.type === 'start' && isPopup) {
    if (state.session?.active) throw Error('A session is already running.');
    const minutes = Number(message.minutes);
    const task = String(message.task || '').trim();
    const domains = state.blocklist || [];
    if (!task || task.length > 160 || !Number.isInteger(minutes) || minutes < 1 || minutes > 480 || !domains.length) throw Error('Add a task, at least one site, and 1–480 whole minutes.');
    const startedAt = Date.now();
    const session = {id: crypto.randomUUID(), active: true, task, plannedMinutes: minutes, startedAt, plannedEnd: startedAt + minutes * 60000, blocklist: domains, blockedCount: 0, countedDocuments: []};
    try {
      await ensureBlocking(session, true);
      await chrome.alarms.create('focus-end', {when: session.plannedEnd});
      // Do not show an active timer until permissions and installed rules are verified.
      await chrome.storage.local.set({session});
    } catch (error) {
      await clearRules();
      await chrome.alarms.clear('focus-end');
      throw error;
    }
    syncStart(session, anonymousId);
  } else if (message.type === 'end' && isPopup) {
    await finish(false);
  } else if (message.type === 'attempt') {
    const session = state.session;
    const url = new URL(sender.url || 'https://invalid.local');
    if (!sender.url?.startsWith(chrome.runtime.getURL('blocked.html') + '?') || url.pathname !== '/blocked.html' || !sender.tab || !sender.documentId) return;
    const domain = url.searchParams.get('domain');
    if (!session?.active || url.searchParams.get('session') !== session.id || !session.blocklist.includes(domain)) return;
    if (!session.countedDocuments.includes(sender.documentId) && !message.reload) {
      const timestamp = new Date().toISOString();
      session.blockedCount++;
      session.countedDocuments.push(sender.documentId);
      await chrome.storage.local.set({session});
      syncAttempt({...session}, domain, timestamp);
    }
  }
  return {...await chrome.storage.local.get(['session', 'summary', 'blocklist']), client_id: anonymousId};
}
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  serial(() => handle(message, sender)).then(state => respond({ok: true, ...state}), error => respond({ok: false, error: error.message}));
  return true;
});
chrome.alarms.onAlarm.addListener(alarm => { if (alarm.name === 'focus-end') serial(reconcile); });
chrome.runtime.onStartup.addListener(() => serial(reconcile));
chrome.runtime.onInstalled.addListener(() => serial(reconcile));
