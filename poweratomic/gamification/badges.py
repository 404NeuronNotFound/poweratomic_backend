BADGES = [
    # --- Consistency tier: total check-ins across all habits ---
    # first_step is folded in as the ladder's first rung (threshold 1)
    # rather than special-cased separately - one less thing to keep in
    # sync with the rest of the tier logic.
    {
        'key': 'first_step',
        'name': 'First Step',
        'description': 'Complete your very first check-in.',
        'category': 'consistency',
        'threshold': 1,
        'unit': 'check-in',
    },
    {
        'key': 'consistency_bronze',
        'name': 'Consistency Hero',
        'description': 'Log 30 check-ins total, across all habits.',
        'category': 'consistency',
        'threshold': 30,
        'unit': 'check-in',
    },
    {
        'key': 'consistency_silver',
        'name': 'Steady Hand',
        'description': 'Log 100 check-ins total, across all habits.',
        'category': 'consistency',
        'threshold': 100,
        'unit': 'check-in',
    },
    {
        'key': 'consistency_gold',
        'name': 'Creature of Habit',
        'description': 'Log 365 check-ins total, across all habits.',
        'category': 'consistency',
        'threshold': 365,
        'unit': 'check-in',
    },
    {
        'key': 'consistency_platinum',
        'name': 'Thousand Days',
        'description': 'Log 1,000 check-ins total, across all habits.',
        'category': 'consistency',
        'threshold': 1000,
        'unit': 'check-in',
    },

    # --- Streak tier: longest_streak on any single habit ---
    {
        'key': 'streak_bronze',
        'name': '7-Day Warrior',
        'description': 'Reach a 7-day streak on any habit.',
        'category': 'streak',
        'threshold': 7,
        'unit': 'day',
    },
    {
        'key': 'streak_silver',
        'name': 'Unstoppable',
        'description': 'Reach a 30-day streak on any habit.',
        'category': 'streak',
        'threshold': 30,
        'unit': 'day',
    },
    {
        'key': 'streak_gold',
        'name': 'Centurion',
        'description': 'Reach a 100-day streak on any habit.',
        'category': 'streak',
        'threshold': 100,
        'unit': 'day',
    },
    {
        'key': 'streak_platinum',
        'name': 'Year One',
        'description': 'Reach a 365-day streak on any habit.',
        'category': 'streak',
        'threshold': 365,
        'unit': 'day',
    },

    # --- One-off: resilience, not perfection. No category/threshold -
    # this is an event (missed a day, came back), not a cumulative value,
    # so "X more to unlock" doesn't apply to it.
    {
        'key': 'comeback_kid',
        'name': 'Comeback Kid',
        'description': 'Check back in on a habit the day after missing one.',
        'category': None,
        'threshold': None,
        'unit': None,
    },

    # --- Focus tier: cumulative completed Pomodoro work-phase hours ---
    {
        'key': 'focus_bronze',
        'name': 'Focused Start',
        'description': 'Complete 5 hours of focus sessions.',
        'category': 'focus',
        'threshold': 5,
        'unit': 'hour',
    },
    {
        'key': 'focus_silver',
        'name': 'Deep Worker',
        'description': 'Complete 25 hours of focus sessions.',
        'category': 'focus',
        'threshold': 25,
        'unit': 'hour',
    },
    {
        'key': 'focus_gold',
        'name': 'Flow State',
        'description': 'Complete 100 hours of focus sessions.',
        'category': 'focus',
        'threshold': 100,
        'unit': 'hour',
    },

    # --- Routine tier: full start-to-finish routine completions ---
    {
        'key': 'routine_bronze',
        'name': 'Routine Runner',
        'description': 'Complete a full routine 5 times.',
        'category': 'routine',
        'threshold': 5,
        'unit': 'routine',
    },
    {
        'key': 'routine_silver',
        'name': 'Creature of Ritual',
        'description': 'Complete a full routine 25 times.',
        'category': 'routine',
        'threshold': 25,
        'unit': 'routine',
    },
    {
        'key': 'routine_gold',
        'name': 'Routine Master',
        'description': 'Complete a full routine 100 times.',
        'category': 'routine',
        'threshold': 100,
        'unit': 'routine',
    },
]

BADGE_BY_KEY = {b['key']: b for b in BADGES}


def get_category_progress(user):
    """
    Single source of truth for "how far is this user into each tiered
    category right now" - used both by the award-checking functions
    below AND by BadgeListView to show progress toward the next tier.
    Previously these values were computed separately in three different
    check_and_award_* functions, which is exactly the kind of duplication
    that caused a real bug earlier in this project - one function, reused
    everywhere, removes that risk entirely.
    """
    from django.db.models import Sum

    from poweratomic.checkins.models import DailyCheckIn
    from poweratomic.checkins.services import compute_habit_stats
    from poweratomic.habits.models import Habit, StackCompletion
    from poweratomic.pomodoro.models import PomodoroSession

    user_habits = list(Habit.objects.filter(user=user))

    total_checkins = DailyCheckIn.objects.filter(user=user).count()

    longest_overall = max(
        (compute_habit_stats(habit)['longest_streak'] for habit in user_habits),
        default=0,
    )

    total_seconds = (
        PomodoroSession.objects.filter(
            user=user, phase=PomodoroSession.Phase.WORK, status=PomodoroSession.Status.COMPLETED
        ).aggregate(total=Sum('planned_duration_seconds'))['total']
        or 0
    )
    total_focus_hours = round(total_seconds / 3600, 1)

    total_routine_completions = StackCompletion.objects.filter(user=user).count()

    return {
        'consistency': total_checkins,
        'streak': longest_overall,
        'focus': total_focus_hours,
        'routine': total_routine_completions,
    }


def check_and_award_badges(user):
    """
    Called after every new check-in. Awards any consistency/streak-tier
    badge whose threshold is now met, generically from the BADGES catalog
    rather than a hardcoded if-chain per tier - the catalog's 'threshold'
    field is the only place that number lives, so there's nothing to keep
    in sync by hand when tiers are added or changed.
    """
    from poweratomic.habits.models import Habit

    from .models import UserBadge

    user_habits = list(Habit.objects.filter(user=user))
    values = get_category_progress(user)

    earned_keys = {
        b['key']
        for b in BADGES
        if b['category'] in ('consistency', 'streak') and values[b['category']] >= b['threshold']
    }

    if _has_comeback(user_habits):
        earned_keys.add('comeback_kid')

    for key in earned_keys:
        UserBadge.objects.get_or_create(user=user, badge_key=key)


def _has_comeback(habits):
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    for habit in habits:
        dates = set(habit.checkins.values_list('date', flat=True))
        if today in dates and yesterday not in dates:
            # Needs at least one check-in older than the gap - otherwise
            # a habit's very first-ever check-in would falsely count as
            # a "comeback" from a missed day that never happened.
            if any(d < yesterday for d in dates):
                return True
    return False


def check_and_award_focus_badges(user):
    """Call this from wherever a PomodoroSession's status is set to
    COMPLETED (not from check-ins - see check_and_award_badges above)."""
    from .models import UserBadge

    values = get_category_progress(user)
    earned_keys = {b['key'] for b in BADGES if b['category'] == 'focus' and values['focus'] >= b['threshold']}

    for key in earned_keys:
        UserBadge.objects.get_or_create(user=user, badge_key=key)


def check_and_award_routine_badges(user):
    """Call this from StackCompleteView after a routine finishes."""
    from .models import UserBadge

    values = get_category_progress(user)
    earned_keys = {b['key'] for b in BADGES if b['category'] == 'routine' and values['routine'] >= b['threshold']}

    for key in earned_keys:
        UserBadge.objects.get_or_create(user=user, badge_key=key)