// Run with: node lock-in-bro/backend/tests/history_sync.test.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../../extension/background.js'), 'utf8');
const recap = {id: 'local-session', task: 'Study', plannedMinutes: 25,
  startedAt: Date.parse('2026-10-04T12:00:00Z'), endedAt: Date.parse('2026-10-04T12:25:00Z'),
  blocklist: ['reddit.com'], actualMinutes: 25, blockedCount: 2, focusScore: 90, completed: true};
function worker(storage, server) {
  const listener = {addListener() {}};
  const context = vm.createContext({console: {warn() {}, error() {}, info() {}},
    importScripts() {}, BACKEND: 'https://example.test', AbortSignal,
    fetch: async (url, options) => server(url, JSON.parse(options.body)),
    chrome: {storage: {local: {
      async get(keys) {
        return structuredClone(Object.fromEntries((Array.isArray(keys) ? keys : [keys])
          .filter(key => key in storage).map(key => [key, storage[key]])));
      },
      async set(values) { Object.assign(storage, structuredClone(values)); }
    }}, alarms: {async create() {}, async clear() {}, onAlarm: listener},
    declarativeNetRequest: {async getDynamicRules() {return []; }},
    runtime: {onMessage: listener, onStartup: listener, onInstalled: listener}}
  });
  vm.runInContext(source, context);
  return {async recover() {
    await vm.runInContext('serial(reconcile)', context);
    await vm.runInContext('networkQueue', context);
  }};
}
(async () => {
  const storage = {client_id: 'client', summary: {...recap}};
  const requests = [];
  let offline = true, failFinish = true;
  const server = async (url, body) => {
    requests.push({url, body});
    if (offline) throw Error('Offline');
    if (url.endsWith('/finish') && failFinish) throw Error('Finish unavailable');
    return {ok: true, async json() {return {session_id: 7}; }};
  };
  await worker(storage, server).recover();
  assert.equal(storage.pendingHistory[recap.id].task, 'Study');
  assert.equal(storage.historySyncError, 'Offline');
  offline = false;
  await worker(storage, server).recover();
  assert.equal(storage.pendingHistory[recap.id].backendSessionId, 7);
  assert.equal(storage.summary.historySynced, undefined);
  failFinish = false;
  const creations = requests.filter(r => r.url.endsWith('/api/sessions')).length;
  const restarted = worker(storage, server);
  await restarted.recover();
  assert.equal(requests.filter(r => r.url.endsWith('/api/sessions')).length, creations);
  assert.deepEqual(storage.pendingHistory, {});
  assert.equal(storage.summary.historySynced, true);
  assert.equal(storage.historySyncError, null);
  const finished = requests.at(-1);
  assert.ok(finished.url.endsWith('/7/finish'));
  assert.equal(finished.body.blocked_count, 2);
  const count = requests.length;
  await restarted.recover();
  assert.equal(requests.length, count);
  console.log('PASS: failed-start recovery, durable finish retry across worker restarts, no repeated upload after success');
})().catch(error => {console.error(error); process.exitCode = 1;});
