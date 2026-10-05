"""Small code-defined catalog and a shared UTC calendar; no scheduled jobs."""
import math
from datetime import datetime, timedelta, timezone, date
from pig import ACCESSORIES


def item(item_id, name, category, cost=0, kind='permanent', *, asset=None, style='classic', slot=None, **metadata):
    return dict(id=item_id, name=name, category=category, cost=cost, kind=kind,
                asset=asset or item_id, style=style, slot=slot or asset or item_id, **metadata)


# Original IDs and XP thresholds are preserved; paid prices are tripled.
LEGACY_ITEMS = tuple(item(key, name, 'accessory', kind='xp', level=level)
                     for level, key, name in ACCESSORIES) + (
    item('laptop', 'Tiny Laptop', 'desk', level=1),
    item('mug', 'Pink Mug', 'desk', 75, level=1),
    item('lamp', 'Heart Lamp', 'desk', 180, level=1),
    item('books', 'Little Book Stack', 'desk', 120, level=1),
    item('poster', 'Heart Poster', 'wall', 105, level=1),
    item('lights', 'Fairy Lights', 'wall', 240, level=1),
    item('plant', 'Desk Plant', 'decor', 150, level=1),
)
WEEKLY_ITEMS = (
    item('bow_lavender', 'Lavender Bow', 'accessory', 270, 'weekly', asset='bow', style='lavender'),
    item('bow_strawberry', 'Strawberry Bow', 'accessory', 330, 'weekly', asset='bow', style='strawberry'),
    item('lamp_cloud', 'Cloud Lamp', 'desk', 390, 'weekly', asset='lamp', style='cloud'),
    item('mug_lavender', 'Lavender Mug', 'desk', 210, 'weekly', asset='mug', style='lavender'),
    item('plant_strawberry', 'Strawberry Pot', 'decor', 300, 'weekly', asset='plant', style='strawberry'),
    item('rug_checker', 'Checkerboard Rug', 'decor', 360, 'weekly', asset='rug', style='checker'),
)
MILESTONE_ITEMS = (
    item('star_glasses', 'Star Glasses', 'accessory', kind='milestone', slot='glasses', milestone='score', target=95, requirement='Complete a session with a focus score of 95+'),
    item('blanket', 'Cozy Blanket', 'decor', kind='milestone', milestone='long_session', target=60, requirement='Complete a session with 60 focused minutes'),
    item('vase', 'Flower Vase', 'decor', kind='milestone', milestone='days', target=3, requirement='Complete sessions on 3 different UTC days'),
    item('pennant', 'Little Victory Pennant', 'wall', kind='milestone', milestone='sessions', target=5, requirement='Complete 5 sessions'),
    item('rug_cloud', 'Cloud Rug', 'decor', kind='milestone', asset='rug', style='cloud', milestone='minutes', target=300, requirement='Complete 300 total focused minutes'),
)
SEASONAL_ITEMS = (
    item('mug_ghost', 'Ghost Mug', 'desk', 270, 'seasonal', asset='mug', style='ghost', season='october', season_label='October'),
    item('mug_cocoa', 'Hot Cocoa', 'desk', 270, 'seasonal', asset='mug', style='cocoa', season='winter', season_label='Winter'),
    item('rug_heart', 'Heart Rug', 'decor', 420, 'seasonal', asset='rug', style='heart', season='valentine', season_label='Valentine'),
    item('plant_tulip', 'Tulip Plant', 'decor', 300, 'seasonal', asset='plant', style='tulip', season='spring', season_label='Spring'),
)
RARE_ITEMS = (
    item('computer_strawberry', 'Strawberry Computer Setup', 'desk', 1800, 'rare', asset='laptop', style='strawberry'),
    item('plushie', 'Giant Pig Plushie', 'decor', 2700, 'rare'),
)
ITEMS = LEGACY_ITEMS + WEEKLY_ITEMS + MILESTONE_ITEMS + SEASONAL_ITEMS + RARE_ITEMS
ITEM_BY_ID = {entry['id']: entry for entry in ITEMS}
SECTIONS = (
    ('permanent', 'Permanent Favorites'), ('weekly', 'This Week’s Finds ✨'),
    ('milestone', 'Earned by Locking In'), ('seasonal', 'Seasonal'),
    ('rare', 'Rare Treats'), ('keepsakes', 'Your Keepsakes'),
)


def shop_calendar(now=None):
    now = now or datetime.now(timezone.utc)
    now = now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now.astimezone(timezone.utc)
    today = now.date()
    monday = today - timedelta(days=today.weekday())
    index = (monday - date(1970, 1, 5)).days // 7
    start = index % len(WEEKLY_ITEMS)
    weekly = [WEEKLY_ITEMS[(start + offset) % len(WEEKLY_ITEMS)]['id'] for offset in range(4)]
    year, week, _ = today.isocalendar()
    return dict(week_key=f'{year}-W{week:02}', weekly_ids=weekly,
                next_rotation=(monday + timedelta(days=7)).isoformat(),
                days_until_rotation=7-today.weekday(), calendar='UTC')


def season_active(season, today):
    return {'october': today.month == 10, 'winter': today.month in (12, 1, 2),
            'valentine': today.month == 2 and today.day <= 14,
            'spring': today.month in (3, 4, 5)}[season]


def milestone_progress(sessions):
    completed = [s for s in sessions if s.completed and s.ended_at]
    def minutes(s):
        value = s.actual_minutes or 0
        return min(480, max(0, value)) if math.isfinite(value) else 0
    def score(s):
        value = s.focus_score or 0
        return min(100, max(0, value)) if math.isfinite(value) else 0
    def utc_day(s):
        value = s.started_at
        return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)).date()
    return dict(sessions=len(completed), minutes=sum(math.floor(minutes(s)) for s in completed),
                score=max((score(s) for s in completed), default=0),
                long_session=max((minutes(s) for s in completed), default=0),
                days=len({utc_day(s) for s in completed}))


def shop_snapshot(sessions, level, purchased, equipped, now=None):
    now = now or datetime.now(timezone.utc)
    now = now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now.astimezone(timezone.utc)
    calendar = shop_calendar(now)
    progress = milestone_progress(sessions)
    entries = []
    for definition in ITEMS:
        kind = definition['kind']
        available = (definition['id'] in calendar['weekly_ids'] if kind == 'weekly' else
                     season_active(definition['season'], now.date()) if kind == 'seasonal' else True)
        earned = (level >= definition['level'] if kind == 'xp' else
                  progress[definition['milestone']] >= definition['target'] if kind == 'milestone' else
                  definition['id'] == 'laptop')
        owned = earned or definition['id'] in purchased
        visible = available or owned
        section = ('keepsakes' if owned and not available else 'permanent' if kind == 'xp' else kind)
        can_buy = available and kind not in ('xp', 'milestone') and not owned
        entry = dict(definition, available=available, owned=owned, unlocked=owned,
                     equipped=owned and definition['id'] in equipped, visible=visible,
                     section=section, can_buy=can_buy)
        if kind == 'milestone':
            entry['progress'] = min(definition['target'], progress[definition['milestone']])
        entries.append(entry)
    calendar['sections'] = [dict(id=key, name=name) for key, name in SECTIONS
                            if any(entry['visible'] and entry['section'] == key for entry in entries)]
    return entries, calendar


def equip_selection(equipped, item_id):
    """Variants share one slot; original unrelated accessories can still coexist."""
    slot = ITEM_BY_ID[item_id]['slot']
    return sorted({key for key in equipped if ITEM_BY_ID[key]['slot'] != slot} | {item_id})
