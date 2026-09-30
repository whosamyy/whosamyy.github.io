const $ = id => document.getElementById(id);
const client = new URLSearchParams(location.search).get('client_id');
const minutes = value => `${Number(value || 0).toFixed(1)} min`;
async function load() {
  if (!client) return;
  $('client').value = client;
  $('status').textContent = 'Loading your focus history…';
  try {
    const response = await fetch(`/api/stats/${encodeURIComponent(client)}`);
    if (!response.ok) throw Error('Could not load your history. Check Flask and refresh.');
    const data = await response.json();
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
  } catch (error) { $('status').textContent = error.message; }
}
load();
