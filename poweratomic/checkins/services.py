from datetime import timedelta

from django.utils import timezone


def compute_habit_stats(habit):
    """
    Returns {current_streak, longest_streak, completion_rate} for a habit,
    computed fresh from its check-in history rather than stored - there's
    only one source of truth (the check-ins themselves), so this can never
    drift out of sync the way a cached counter could.
    """
    dates_desc = list(habit.checkins.order_by('-date').values_list('date', flat=True))
    today = timezone.localdate()

    return {
        'current_streak': _current_streak(dates_desc, today),
        'longest_streak': _longest_streak(dates_desc),
        'completion_rate': _completion_rate(habit, len(dates_desc), today),
    }


def _current_streak(dates_desc, today):
    """
    Consecutive days ending at the most recent check-in. A streak still
    counts as "current" if the most recent check-in was yesterday (today
    isn't over yet), but breaks if it's any older than that.
    """
    if not dates_desc:
        return 0

    most_recent = dates_desc[0]
    if most_recent not in (today, today - timedelta(days=1)):
        return 0

    streak = 1
    expected = most_recent - timedelta(days=1)
    for d in dates_desc[1:]:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


def _longest_streak(dates_desc):
    """Longest run of consecutive days anywhere in the history, not just the current one."""
    if not dates_desc:
        return 0

    dates_asc = sorted(dates_desc)
    longest = current = 1
    for prev, curr in zip(dates_asc, dates_asc[1:]):
        if curr == prev + timedelta(days=1):
            current += 1
        else:
            current = 1
        longest = max(longest, current)
    return longest


def _completion_rate(habit, checkin_count, today):
    """% of days since the habit was created that have a check-in, capped at 100."""
    days_tracked = max((today - habit.created_at.date()).days + 1, 1)
    return min(round((checkin_count / days_tracked) * 100), 100)