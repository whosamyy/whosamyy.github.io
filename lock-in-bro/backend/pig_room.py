"""Account-owned cosmetics; XP and earned coins always come from focus history.

Priority and thresholds are documented in PIG_WORLD.md. No focus rows are mutated.
"""
import math
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pig import ACCESSORIES, pig_progress

ITEMS = tuple(
    dict(id=item, name=name, category='accessory', level=level, cost=0)
    for level, item, name in ACCESSORIES
) + (
    dict(id='laptop', name='Tiny Laptop', category='desk', cost=0, level=1),
    dict(id='mug', name='Pink Mug', category='desk', cost=25, level=1),
    dict(id='lamp', name='Heart Lamp', category='desk', cost=60, level=1),
    dict(id='books', name='Little Book Stack', category='desk', cost=40, level=1),
    dict(id='poster', name='Heart Poster', category='wall', cost=35, level=1),
    dict(id='lights', name='Fairy Lights', category='wall', cost=80, level=1),
    dict(id='plant', name='Desk Plant', category='decor', cost=50, level=1),
)
ITEM_BY_ID = {item['id']: item for item in ITEMS}
MESSAGES = dict(happy='piggy is proud of you 💗', proud='academic weapon behavior',
                cozy='we’re locked in and comfy', sleepy='piggy needs a tiny coffee ☕',
                distracted='a tiny detour? piggy saved your seat 💗',
                excited='new little win unlocked!! ✨')


def utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def local_zone(name):
    try:
        return ZoneInfo(name or 'UTC')
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return ZoneInfo('UTC')


def recent_context(sessions, now=None, zone='UTC'):
    now = utc(now or datetime.now(timezone.utc))
    finished = sorted((s for s in sessions if s.ended_at), key=lambda s: (utc(s.ended_at), s.id), reverse=True)
    recent = [s for s in finished if now - timedelta(hours=48) <= utc(s.ended_at) <= now]
    latest = recent[0] if recent else None
    completed = [s for s in recent if s.completed]
    milestone = False
    if latest and latest.completed:
        before = [s for s in sessions if s.id != latest.id]
        milestone = (pig_progress(sessions)['level'] > pig_progress(before)['level'] or
                     (sum(s.completed and bool(s.ended_at) for s in sessions) % 5 == 0))
    night = bool(latest and (utc(latest.started_at).astimezone(local_zone(zone)).hour >= 21 or
                            utc(latest.started_at).astimezone(local_zone(zone)).hour < 6))
    return latest, completed, milestone, night


def determine_pig_mood(sessions, now=None, zone='UTC', unlocked_something=False):
    latest, completed, milestone, night = recent_context(sessions, now, zone)
    if unlocked_something or milestone:
        return 'excited'
    if not latest:
        return 'sleepy'
    if latest.blocked_count >= 5:
        return 'distracted'
    if night or (latest.actual_minutes or 0) < 5:
        return 'sleepy'
    score = latest.focus_score or 0
    if latest.completed and (score >= 90 or len(completed) >= 3):
        return 'proud'
    if latest.completed and score >= 70 and latest.blocked_count <= 2:
        return 'happy'
    return 'cozy'


def determine_focus_weather(sessions, now=None, zone='UTC', unlocked_something=False):
    latest, _, milestone, night = recent_context(sessions, now, zone)
    if unlocked_something or milestone or (latest and latest.completed and (latest.focus_score or 0) >= 98):
        return 'sparkle'
    if night:
        return 'night'
    if latest and (latest.blocked_count >= 5 or (latest.focus_score is not None and latest.focus_score < 50)):
        return 'rainy'
    if latest and latest.completed and (latest.focus_score or 0) >= 90 and latest.blocked_count <= 2:
        return 'sunny'
    return 'cloudy'


def earned_coins(sessions):
    total = 0
    for s in sessions:
        if s.completed and s.ended_at:
            minutes = s.actual_minutes or 0
            total += math.floor(min(480, max(0, minutes))) if math.isfinite(minutes) else 0
    return total


def room_state(sessions, profile=None, now=None, zone='UTC', unlocked_something=False):
    state = pig_progress(sessions)
    legacy = {item['id'] for item in state['unlocked_items']}
    purchased = set(profile.purchased_items or []) if profile else set()
    unlocked = legacy | purchased | {'laptop'}
    # None is a deliberate legacy-compatible default. [] means unequipped by user.
    equipped = (profile.equipped_items if profile and profile.equipped_items is not None
                else sorted(legacy | {'laptop'}))
    state.update(coins=max(0, earned_coins(sessions) - (profile.coins_spent if profile else 0)),
                 earned_coins=earned_coins(sessions), equipped_items=sorted(set(equipped) & unlocked),
                 mood=determine_pig_mood(sessions, now, zone, unlocked_something),
                 weather=determine_focus_weather(sessions, now, zone, unlocked_something),
                 timezone=local_zone(zone).key,
                 items=[dict(item, unlocked=item['id'] in unlocked, equipped=item['id'] in equipped)
                        for item in ITEMS])
    state['message'] = MESSAGES[state['mood']]
    if unlocked_something:
        state['message'] = 'NEW ITEM UNLOCKED!! ✨'
    return state
