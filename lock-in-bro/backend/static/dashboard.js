const $ = id => document.getElementById(id);
const minutes = value => `${Number(value || 0).toFixed(1)} min`;
let loading = false;
let pigState = null;
let roomBusy = false;
let roomRevision = 0;
let celebrationUntil = 0;
const zoneQuery = `?timezone=${encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC')}`;
const weatherNames = {sunny: 'Soft sunshine', cloudy: 'Soft clouds', rainy: 'Cozy rain', night: 'Star night', sparkle: 'Sparkle skies'};
function applyFocusWeather(weather) {
  // One resolved state drives the room and the page, including celebrations.
  const state = Object.hasOwn(weatherNames, weather) ? weather : 'cloudy';
  document.body.dataset.weather = state;
  document.querySelector('.pig-art').dataset.weather = state;
  return state;
}
function renderPig(pig) {
  $('pig-level').textContent = `Level ${pig.level}`;
  $('pig-xp').textContent = `XP: ${pig.level_xp} / ${pig.xp_to_level}`;
  $('pig-progress').value = pig.level_xp;
  $('pig-progress').max = pig.xp_to_level;
  $('pig-total').textContent = `${pig.total_xp.toLocaleString()} total XP · grows with your completed sessions`;
  pigState = pig;
  const celebrating = Date.now() < celebrationUntil;
  const mood = celebrating ? 'excited' : pig.mood;
  const weather = applyFocusWeather(celebrating ? 'sparkle' : pig.weather);
  $('pig-message').textContent = celebrating ? 'NEW ITEM UNLOCKED!! ✨' : pig.message;
  document.querySelector('.pig-art').dataset.mood = mood;
  $('pig-mood').textContent = `Mood: ${mood[0].toUpperCase() + mood.slice(1)}`;
  $('pig-weather').textContent = weatherNames[weather];
  $('room-description').textContent = `Your ${mood} pig at a cozy study desk, with ${weatherNames[weather].toLowerCase()} through the window and your equipped decorations.`;
  $('pig-coins').textContent = `${pig.coins.toLocaleString()} focus coins`;
  $('customizer-coins').textContent = `${pig.coins.toLocaleString()} coins to make it cozy`;
  $('customize-pig').disabled = false;
  $('pig-unlocks').replaceChildren();
  for (const item of pig.unlocked_items) {
    const badge = document.createElement('li'); badge.textContent = item.name;
    $('pig-unlocks').append(badge);
  }
  if (!pig.unlocked_items.length) {
    const item = document.createElement('li'); item.textContent = 'A little pig. A big future.';
    $('pig-unlocks').append(item);
  }
  const unlocked = new Set(pig.equipped_items);
  document.querySelectorAll('[data-pig-item]').forEach(item => {
    item.setAttribute('display', unlocked.has(item.dataset.pigItem) ? 'inline' : 'none');
  });
  $('pig-next').textContent = pig.next_unlock
    ? `${pig.next_unlock.xp_remaining} XP until ${pig.next_unlock.name} at level ${pig.next_unlock.level}`
    : 'Every XP goodie unlocked. Keep that lock-in energy 💖';
  updateItemCards(pig);
}
const previewBoxes = {
  sparkles: '35 90 260 80', bow: '174 35 82 78', headphones: '45 50 231 138',
  strawberry: '186 190 55 77', glasses: '78 108 165 60', laptop: '170 218 124 70',
  mug: '276 221 65 65', lamp: '315 180 109 109', books: '108 247 63 38',
  poster: '32 62 85 102', lights: '19 20 444 53', plant: '29 227 76 116'
};
function itemPreview(item) {
  const preview = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  preview.setAttribute('viewBox', previewBoxes[item.id]);
  preview.setAttribute('aria-hidden', 'true');
  preview.classList.add('item-preview');
  const source = document.querySelector(`[data-pig-item="${item.id}"]`);
  if (source) {
    const copy = source.cloneNode(true);
    copy.removeAttribute('data-pig-item');
    copy.removeAttribute('display');
    if (item.id === 'strawberry') copy.removeAttribute('transform');
    // The lamp's translucent light cone refers to the existing SVG gradient.
    preview.append(copy);
  }
  return preview;
}
function updateItemCards(pig) {
  // Reuse controls across polls so keyboard focus never disappears on refresh.
  for (const item of pig.items) {
    let card = $('pig-item-cards').querySelector(`[data-item-card="${item.id}"]`);
    if (!card) {
      card = document.createElement('article');
      card.className = 'pig-item-card'; card.dataset.itemCard = item.id;
      const name = document.createElement('h3'); name.textContent = item.name;
      const status = document.createElement('p'); status.className = 'item-state';
      const button = document.createElement('button'); button.type = 'button';
      button.addEventListener('click', () => customizeItem(item.id));
      card.append(itemPreview(item), name, status, button);
      $('pig-item-cards').append(card);
    }
    card.querySelector('.item-state').textContent = item.equipped ? 'Equipped · looking cozy' : item.unlocked ? 'Unlocked' : item.category === 'accessory' ? `Unlocks at level ${item.level}` : `${item.cost} coins`;
    const button = card.querySelector('button');
    button.textContent = item.unlocked ? (item.equipped ? 'Unequip' : 'Equip') : item.category === 'accessory' ? `Level ${item.level}` : 'Unlock';
    button.setAttribute('aria-label', `${button.textContent} ${item.name}`);
    button.disabled = roomBusy || (!item.unlocked && (item.category === 'accessory' || pig.coins < item.cost));
  }
}
async function customizeItem(id) {
  if (roomBusy || !pigState) return;
  const item = pigState.items.find(item => item.id === id);
  roomBusy = true;
  roomRevision += 1;
  updateItemCards(pigState);
  $('customizer-status').textContent = 'Making it cozy…';
  try {
    const action = item.unlocked ? 'equip' : 'unlock';
    const payload = {item_id: id};
    if (item.unlocked) payload.equipped = !item.equipped;
    const response = await fetch(`/api/me/pig/${action}` + zoneQuery, {
      method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content},
      body: JSON.stringify(payload), signal: AbortSignal.timeout(15000)
    });
    if (response.status === 401) { location.replace('/login'); return; }
    const result = await response.json();
    if (!response.ok) throw Error(result.error || 'Could not save your room. Please try again.');
    if (action === 'unlock') celebrationUntil = Date.now() + 15000;
    roomBusy = false;
    renderPig(result.pig);
    $('customizer-status').textContent = action === 'unlock' ? `${item.name} unlocked! Equip it whenever you like.` : `${item.name} ${payload.equipped ? 'equipped' : 'put away'}. Saved to your account.`;
  } catch (error) { $('customizer-status').textContent = error.message; }
  finally { roomBusy = false; if (pigState) updateItemCards(pigState); }
}
$('customize-pig').addEventListener('click', () => $('pig-customizer').showModal());
$('close-customizer').addEventListener('click', () => $('pig-customizer').close());
$('pig-customizer').addEventListener('close', () => $('customize-pig').focus());
$('pig-customizer').addEventListener('keydown', event => {
  if (event.key !== 'Tab') return;
  const controls = [...$('pig-customizer').querySelectorAll('button:not(:disabled)')];
  const first = controls[0], last = controls[controls.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault(); last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault(); first.focus();
  }
});

async function load() {
  if (loading) return;
  loading = true;
  const pigRevision = roomRevision;
  $('status').textContent = 'Loading your focus history…';
  try {
    const response = await fetch('/api/me/stats' + zoneQuery, {
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
    if (!roomBusy && pigRevision === roomRevision) renderPig(data.pig);
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
