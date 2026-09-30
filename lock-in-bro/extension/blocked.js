const params = new URLSearchParams(location.search);
let session;
function paint() {
  const active = session?.active && session.id === params.get('session') && Date.now() < session.plannedEnd;
  document.getElementById('task').textContent = active ? `You are studying: ${session.task}` : 'This focus session has ended.';
  const seconds = active ? Math.max(0, Math.ceil((session.plannedEnd - Date.now()) / 1000)) : 0;
  document.getElementById('timer').textContent = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  document.getElementById('domain').textContent = `You tried to open ${params.get('domain') || 'a paused site'}`;
  if (!active) document.getElementById('status').textContent = 'Sites are available again. Navigate to the site when you are ready.';
}
async function refresh(type = 'state') {
  try {
    const response = await chrome.runtime.sendMessage({type, reload: performance.getEntriesByType('navigation')[0]?.type === 'reload'});
    if (!response.ok) throw Error(response.error);
    session = response.session; paint();
  } catch (error) { document.getElementById('status').textContent = error.message; }
}
document.getElementById('back').onclick = async () => {
  try { await chrome.tabs.update({url: 'chrome://newtab/'}); }
  catch (error) { document.getElementById('status').textContent = error.message; }
};
chrome.storage.onChanged.addListener(() => refresh());
refresh('attempt');
setInterval(() => { paint(); if (session?.active && Date.now() >= session.plannedEnd) refresh(); }, 1000);
