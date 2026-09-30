// All state changes run in one queue, so simultaneous tabs cannot lose counts.
let queue = Promise.resolve();
function serial(work) {
  const result = queue.then(work);
  queue = result.catch(console.error);
  return result;
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
  delete summary.countedDocuments;
  await chrome.storage.local.set({session: null, summary});
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
  if (message.type === 'state') return state;
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
  } else if (message.type === 'end' && isPopup) {
    await finish(false);
  } else if (message.type === 'attempt') {
    const session = state.session;
    const url = new URL(sender.url || 'https://invalid.local');
    if (!sender.url.startsWith(chrome.runtime.getURL('blocked.html') + '?') || url.pathname !== '/blocked.html' || !sender.tab || !sender.documentId) return;
    const domain = url.searchParams.get('domain');
    if (!session?.active || url.searchParams.get('session') !== session.id || !session.blocklist.includes(domain)) return;
    if (!session.countedDocuments.includes(sender.documentId) && !message.reload) {
      session.blockedCount++;
      session.countedDocuments.push(sender.documentId);
      await chrome.storage.local.set({session});
    }
  }
  return await chrome.storage.local.get(['session', 'summary', 'blocklist']);
}
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  serial(() => handle(message, sender)).then(state => respond({ok: true, ...state}), error => respond({ok: false, error: error.message}));
  return true;
});
chrome.alarms.onAlarm.addListener(alarm => { if (alarm.name === 'focus-end') serial(reconcile); });
chrome.runtime.onStartup.addListener(() => serial(reconcile));
chrome.runtime.onInstalled.addListener(() => serial(reconcile));
