const $ = id => document.getElementById(id);
const minutes = value => `${Number(value || 0).toFixed(1)} min`;
let loading = false;
function renderPig(pig) {
  $('pig-level').textContent = `Level ${pig.level}`;
  $('pig-xp').textContent = `XP: ${pig.level_xp} / ${pig.xp_to_level}`;
  $('pig-progress').value = pig.level_xp;
  $('pig-progress').max = pig.xp_to_level;
  $('pig-total').textContent = `${pig.total_xp.toLocaleString()} total XP · grows with your completed sessions`;
  $('pig-message').textContent = pig.message;
  $('pig-unlocks').replaceChildren();
  for (const item of pig.unlocked_items) {
    const badge = document.createElement('li'); badge.textContent = item.name;
    $('pig-unlocks').append(badge);
  }
  if (!pig.unlocked_items.length) {
    const item = document.createElement('li'); item.textContent = 'A little pig. A big future.';
    $('pig-unlocks').append(item);
  }
  const unlocked = new Set(pig.unlocked_items.map(item => item.id));
  document.querySelectorAll('[data-pig-item]').forEach(item => {
    item.setAttribute('display', unlocked.has(item.dataset.pigItem) ? 'inline' : 'none');
  });
  $('pig-next').textContent = pig.next_unlock
    ? `${pig.next_unlock.xp_remaining} XP until ${pig.next_unlock.name} at level ${pig.next_unlock.level}`
    : 'Every goodie unlocked. Keep that lock-in energy 💖';
}
async function load() {
  if (loading) return;
  loading = true;
  $('status').textContent = 'Loading your focus history…';
  try {
    const response = await fetch('/api/me/stats', {
      cache: 'no-store', signal: AbortSignal.timeout(15000)
    });
    if (response.status === 401) {
      // Clear any visible history before navigating after session expiry.
      for (const id of ['sessions', 'domains', 'chart']) $(id).replaceChildren();
      for (const id of ['minutes', 'completed', 'blocked', 'score', 'session-count']) $(id).textContent = '—';
      document.querySelector('.pig-panel').hidden = true;
      location.replace('/login');
      return;
    }
    if (!response.ok) throw Error('Could not load your history. Check Flask and refresh.');
    const data = await response.json();
    renderPig(data.pig);
    // Each refresh replaces the previous snapshot, including empty states.
    for (const id of ['sessions', 'domains', 'chart']) $(id).replaceChildren();
    $('status').textContent = data.total_sessions ? 'Every focused minute counts. Keep going.' : 'No sessions yet. Start one in the extension, then come back here!';
    $('minutes').textContent = minutes(data.total_focus_minutes);
    $('completed').textContent = data.completed_sessions;
    $('blocked').textContent = data.total_blocked_attempts;
    $('score').textContent = data.average_focus_score === null ? 'Not scored yet' : data.average_focus_score.toFixed(1);
    $('session-count').textContent = `${data.total_sessions} total sessions · Average finished session: ${minutes(data.average_session_length)} · Showing latest 20`;
    for (const session of data.recent_sessions) {
      const row = document.createElement('tr');
      for (const value of [session.task, minutes(session.planned_minutes), session.actual_minutes === null ? '—' : minutes(session.actual_minutes), session.blocked_count, session.focus_score ?? '—', !session.ended_at ? 'In progress' : session.completed ? 'Completed' : 'Ended early', new Date(session.started_at).toLocaleString()]) {
        const cell = document.createElement('td'); cell.textContent = value; row.append(cell);
      }
      $('sessions').append(row);
    }
    for (const item of data.most_blocked_domains) {
      const li = document.createElement('li'); li.textContent = `${item.domain} — ${item.count}`; $('domains').append(li);
    }
    if (!data.most_blocked_domains.length) $('domains').textContent = 'No recorded distractions. Nice work.';
    // A dependency-free bar chart: no CDN, tracking, or network requirement.
    const days = data.focus_by_day.slice(-30);
    const max = Math.max(1, ...days.map(d => d.minutes));
    $('chart').setAttribute('aria-label', days.length ? days.map(d => `${d.day}: ${minutes(d.minutes)}`).join('; ') : 'No finished sessions yet');
    for (const day of days) {
      const column = document.createElement('div'); column.className = 'column';
      const label = document.createElement('span'); label.textContent = minutes(day.minutes);
      const bar = document.createElement('div'); bar.className = 'bar'; bar.style.height = `${day.minutes / max * 150}px`;
      const date = document.createElement('span'); date.textContent = day.day.slice(5);
      column.append(label, bar, date); $('chart').append(column);
    }
    if (!days.length) $('chart').textContent = 'Your first finished session will start this chart.';
  } catch (error) { $('status').textContent = `${error.message} Retrying automatically…`; }
  finally { loading = false; }
}
load();
// Keep an open dashboard current when a session finishes in the extension.
setInterval(() => { if (!document.hidden) load(); }, 5000);
document.addEventListener('visibilitychange', () => { if (!document.hidden) load(); });
window.addEventListener('focus', load);
