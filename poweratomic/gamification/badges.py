BADGES = [
    {
        'key': 'first_step',
        'name': 'First Step',
        'description': 'Complete your very first check-in.',
    },
    {
        'key': 'seven_day_warrior',
        'name': '7-Day Warrior',
        'description': 'Reach a 7-day streak on any habit.',
    },
    {
        'key': 'consistency_hero',
        'name': 'Consistency Hero',
        'description': 'Log 30 check-ins total, across all habits.',
    },
    {
        'key': 'unstoppable',
        'name': 'Unstoppable',
        'description': 'Reach a 30-day streak on any habit.',
    },
]

BADGE_BY_KEY = {b['key']: b for b in BADGES}


def check_and_award_badges(user):
    """
    Called after every new check-in. Recomputes from scratch each time
    rather than tracking incremental state - with these data volumes
    that's cheap, and it means there's no separate counter that could
    drift out of sync with what actually happened.
    """
    from poweratomic.checkins.models import DailyCheckIn
    from poweratomic.checkins.services import compute_habit_stats
    from poweratomic.habits.models import Habit

    from .models import UserBadge

    total_checkins = DailyCheckIn.objects.filter(user=user).count()
    longest_overall = max(
        (compute_habit_stats(habit)['longest_streak'] for habit in Habit.objects.filter(user=user)),
        default=0,
    )

    earned_keys = set()
    if total_checkins >= 1:
        earned_keys.add('first_step')
    if total_checkins >= 30:
        earned_keys.add('consistency_hero')
    if longest_overall >= 7:
        earned_keys.add('seven_day_warrior')
    if longest_overall >= 30:
        earned_keys.add('unstoppable')

    for key in earned_keys:
        UserBadge.objects.get_or_create(user=user, badge_key=key)