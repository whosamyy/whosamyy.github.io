"""Deterministic rewards derived from existing completed focus sessions."""
import math

ACCESSORIES = (
    (2, 'sparkles', 'Sparkle Blush'),
    (3, 'bow', 'Pink Bow'),
    (5, 'headphones', 'Cozy Headphones'),
    (7, 'strawberry', 'Tiny Strawberry'),
    (10, 'glasses', 'Heart Glasses'),
)


def pig_progress(sessions):
    total = 0
    for session in sessions:
        if not session.completed or session.ended_at is None:
            continue
        minutes = session.actual_minutes or 0
        score = session.focus_score or 0
        minutes = min(480, max(0, minutes)) if math.isfinite(minutes) else 0
        score = min(100, max(0, score)) if math.isfinite(score) else 0
        total += 10 + math.floor(minutes) + math.floor(score / 10)
    level = 1 + total // 100
    unlocked = [{'id': item, 'name': name, 'level': threshold}
                for threshold, item, name in ACCESSORIES if level >= threshold]
    upcoming = next(({'name': name, 'level': threshold, 'xp_remaining': (threshold - 1) * 100 - total}
                     for threshold, _, name in ACCESSORIES if level < threshold), None)
    return dict(total_xp=total, level=level, level_xp=total % 100, xp_to_level=100,
                unlocked_items=unlocked, next_unlock=upcoming,
                message='piggy is ready for your first lock-in 💖' if total == 0 else
                        'academic weapon energy 💖' if level >= 10 else 'piggy is proud of you 💖')
