const $ = id => document.getElementById(id);
let state = {};
async function send(message) {
  const response = await chrome.runtime.sendMessage(message);
  if (!response?.ok) throw Error(response?.error || 'Could not reach the background worker.');
  state = response;
  render();
}
function showError(error) { $('error').textContent = error.message; }
function normalize(value) {
  const url = new URL(value.includes('://') ? value.trim() : 'https://' + value.trim());
  if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password) throw Error('Use a website domain or an http/https URL.');
  const domain = url.hostname.toLowerCase().replace(/^www\./, '').replace(/\.$/, '');
  if (!/^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/.test(domain)) throw Error('Enter a domain like reddit.com.');
  return domain;
}
function render() {
  $('dashboard-link').href = `${BACKEND}/?client_id=${encodeURIComponent(state.client_id || '')}`;
  const session = state.session;
  $('setup').hidden = !!session?.active;
  $('active').hidden = !session?.active;
  $('sites').replaceChildren();
  for (const domain of state.blocklist || []) {
    const item = document.createElement('li');
    const name = document.createElement('span'); name.textContent = domain;
    const button = document.createElement('button'); button.textContent = 'Remove';
    button.setAttribute('aria-label', `Remove ${domain}`);
    button.onclick = () => send({type: 'save', domains: state.blocklist.filter(d => d !== domain)}).catch(showError);
    item.append(name, button); $('sites').append(item);
  }
  if (session?.active) {
    $('current-task').textContent = session.task;
    $('count').textContent = session.blockedCount;
    tick();
  }
  const summary = state.summary;
  $('summary').hidden = !summary || !!session?.active;
  if (summary) {
    $('summary-task').textContent = summary.task;
    const seconds = Math.max(0, Math.floor((summary.endedAt - summary.startedAt) / 1000));
    $('summary-details').textContent = `${summary.completed ? 'Completed' : 'Ended early'} · Planned ${summary.plannedMinutes} min · Actual ${Math.floor(seconds / 60)}m ${seconds % 60}s · ${summary.blockedCount} blocked attempts · Score: ${summary.focusScore ?? "Not scored yet"}`;
  }
}
let refreshing = false;
function tick() {
  if (!state.session?.active) return;
  const seconds = Math.max(0, Math.ceil((state.session.plannedEnd - Date.now()) / 1000));
  $('timer').textContent = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  if (!seconds && !refreshing) {
    refreshing = true;
    send({type: 'state'}).catch(showError).finally(() => { refreshing = false; });
  }
}
$('duration').onchange = () => { $('custom').hidden = $('duration').value !== 'custom'; };
$('add-form').onsubmit = async event => {
  event.preventDefault(); $('error').textContent = '';
  try {
    const domain = normalize($('domain').value);
    if ((state.blocklist || []).includes(domain)) throw Error('That site is already on your list.');
    await send({type: 'save', domains: [...(state.blocklist || []), domain]});
    $('domain').value = '';
  } catch (error) { showError(error); }
};
$('start').onclick = async () => {
  $('error').textContent = ''; $('start').disabled = true;
  try {
    const minutes = Number($('duration').value === 'custom' ? $('custom').value : $('duration').value);
    const task = $('task').value.trim();
    if (!task || !Number.isInteger(minutes) || minutes < 1 || minutes > 480 || !state.blocklist?.length) throw Error('Enter a task, 1–480 whole minutes, and at least one site.');
    // Request only chosen sites, directly from this button's user gesture.
    const origins = state.blocklist.flatMap(d => [`http://*.${d}/*`, `https://*.${d}/*`]);
    console.info('[Lock In Bro] Requesting chosen-site access', {blocklist: state.blocklist, origins});
    const granted = await chrome.permissions.request({origins});
    console.info('[Lock In Bro] Permission request result', {granted});
    if (!granted) throw Error('Allow access to your chosen sites to start blocking.');
    const confirmed = await chrome.permissions.contains({origins});
    console.info('[Lock In Bro] Permission confirmation', {confirmed});
    if (!confirmed) throw Error('Chrome has not granted the required website access. Try starting again.');
    await send({type: 'start', task, minutes});
  } catch (error) {
    // Promise rejection contains the Chrome API error (no callback lastError needed).
    console.error('[Lock In Bro] Session start failed:', error);
    showError(error);
  }
  finally { $('start').disabled = false; }
};
$('end').onclick = () => send({type: 'end'}).catch(showError);
chrome.storage.onChanged.addListener(() => send({type: 'state'}).catch(showError));
send({type: 'state'}).catch(showError);
setInterval(tick, 1000);
