// All state changes run in one queue, so simultaneous tabs cannot lose counts.
let queue = Promise.resolve();
function serial(work) {
  const result = queue.then(work);
  queue = result.catch(console.error);
  return result;
}
async function clearRules() {
  const rules = await chrome.declarativeNetRequest.getDynamicRules();
  await chrome.declarativeNetRequest.updateDynamicRules({removeRuleIds: rules.map(r => r.id)});
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
  else if (session?.active) await chrome.alarms.create('focus-end', {when: session.plannedEnd});
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
    const origins = domains.flatMap(d => [`http://*.${d}/*`, `https://*.${d}/*`]);
    if (!await chrome.permissions.contains({origins})) throw Error('Website access is required to block your chosen sites.');
    const startedAt = Date.now();
    const session = {id: crypto.randomUUID(), active: true, task, plannedMinutes: minutes, startedAt, plannedEnd: startedAt + minutes * 60000, blocklist: domains, blockedCount: 0, countedDocuments: []};
    await chrome.storage.local.set({session});
    try {
      await chrome.declarativeNetRequest.updateDynamicRules({addRules: domains.map((domain, i) => ({
        id: i + 1, priority: 1,
        action: {type: 'redirect', redirect: {url: chrome.runtime.getURL(`blocked.html?domain=${encodeURIComponent(domain)}&session=${session.id}`)}},
        condition: {requestDomains: [domain], resourceTypes: ['main_frame']}
      }))});
      await chrome.alarms.create('focus-end', {when: session.plannedEnd});
    } catch (error) { await finish(false); throw error; }
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
