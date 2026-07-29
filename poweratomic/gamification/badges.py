BADGES = [
    {
        'key': 'first_step',
        'name': 'First Step',
        'description': 'Complete your very first check-in.',
    },

    # --- Streak tier: longest_streak on any single habit ---
    {
        'key': 'streak_bronze',
        'name': '7-Day Warrior',
        'description': 'Reach a 7-day streak on any habit.',
    },
    {
        'key': 'streak_silver',
        'name': 'Unstoppable',
        'description': 'Reach a 30-day streak on any habit.',
    },
    {
        'key': 'streak_gold',
        'name': 'Centurion',
        'description': 'Reach a 100-day streak on any habit.',
    },
    {
        'key': 'streak_platinum',
        'name': 'Year One',
        'description': 'Reach a 365-day streak on any habit.',
    },

    # --- Consistency tier: total check-ins across all habits ---
    {
        'key': 'consistency_bronze',
        'name': 'Consistency Hero',
        'description': 'Log 30 check-ins total, across all habits.',
    },
    {
        'key': 'consistency_silver',
        'name': 'Steady Hand',
        'description': 'Log 100 check-ins total, across all habits.',
    },
    {
        'key': 'consistency_gold',
        'name': 'Creature of Habit',
        'description': 'Log 365 check-ins total, across all habits.',
    },
    {
        'key': 'consistency_platinum',
        'name': 'Thousand Days',
        'description': 'Log 1,000 check-ins total, across all habits.',
    },

    # --- One-off: resilience, not perfection ---
    {
        'key': 'comeback_kid',
        'name': 'Comeback Kid',
        'description': 'Check back in on a habit the day after missing one.',
    },

    # --- Focus tier: cumulative completed Pomodoro work-phase minutes ---
    {
        'key': 'focus_bronze',
        'name': 'Focused Start',
        'description': 'Complete 5 hours of focus sessions.',
    },
    {
        'key': 'focus_silver',
        'name': 'Deep Worker',
        'description': 'Complete 25 hours of focus sessions.',
    },
    {
        'key': 'focus_gold',
        'name': 'Flow State',
        'description': 'Complete 100 hours of focus sessions.',
    },

    # --- Routine tier: full start-to-finish routine completions ---
    {
        'key': 'routine_bronze',
        'name': 'Routine Runner',
        'description': 'Complete a full routine 5 times.',
    },
    {
        'key': 'routine_silver',
        'name': 'Creature of Ritual',
        'description': 'Complete a full routine 25 times.',
    },
    {
        'key': 'routine_gold',
        'name': 'Routine Master',
        'description': 'Complete a full routine 100 times.',
    },
]

BADGE_BY_KEY = {b['key']: b for b in BADGES}


def check_and_award_badges(user):
    """
    Called after every new check-in. Recomputes from scratch each time
    rather than tracking incremental state - with these data volumes
    that's cheap, and it means there's no separate counter that could
    drift out of sync with what actually happened.

    Focus-time badges are NOT checked here - see
    check_and_award_focus_badges() below, which needs to be called from
    wherever a PomodoroSession is marked completed, not from check-ins.
    """
    from poweratomic.checkins.models import DailyCheckIn
    from poweratomic.checkins.services import compute_habit_stats
    from poweratomic.habits.models import Habit

    from .models import UserBadge

    user_habits = list(Habit.objects.filter(user=user))
    total_checkins = DailyCheckIn.objects.filter(user=user).count()
    longest_overall = max(
        (compute_habit_stats(habit)['longest_streak'] for habit in user_habits),
        default=0,
    )

    earned_keys = set()

    if total_checkins >= 1:
        earned_keys.add('first_step')

    # Streak tier
    if longest_overall >= 7:
        earned_keys.add('streak_bronze')
    if longest_overall >= 30:
        earned_keys.add('streak_silver')
    if longest_overall >= 100:
        earned_keys.add('streak_gold')
    if longest_overall >= 365:
        earned_keys.add('streak_platinum')

    # Consistency tier
    if total_checkins >= 30:
        earned_keys.add('consistency_bronze')
    if total_checkins >= 100:
        earned_keys.add('consistency_silver')
    if total_checkins >= 365:
        earned_keys.add('consistency_gold')
    if total_checkins >= 1000:
        earned_keys.add('consistency_platinum')

    # Comeback: any habit checked in today, not checked in yesterday, but
    # with check-in history predating the gap - excludes brand-new habits
    # whose very first check-in would otherwise trivially qualify.
    if _has_comeback(user_habits):
        earned_keys.add('comeback_kid')

    for key in earned_keys:
        UserBadge.objects.get_or_create(user=user, badge_key=key)


def check_and_award_routine_badges(user):
    """Call this from StackCompleteView after a routine finishes.

    Counts StackCompletion rows directly rather than anything on
    HabitStack itself - this survives a stack being deleted later,
    since StackCompletion keeps its own denormalized stack_name and
    SET_NULLs its stack FK instead of cascading away.
    """
    from poweratomic.habits.models import StackCompletion

    from .models import UserBadge

    total = StackCompletion.objects.filter(user=user).count()

    earned_keys = set()
    if total >= 5:
        earned_keys.add('routine_bronze')
    if total >= 25:
        earned_keys.add('routine_silver')
    if total >= 100:
        earned_keys.add('routine_gold')

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
    """
    Call this from wherever a PomodoroSession's status is set to
    COMPLETED (not from check-ins - see check_and_award_badges above).

    planned_duration_seconds on a COMPLETED work-phase session is a
    reliable stand-in for actual focus time: completePhase() on the
    frontend only marks a session completed once the full planned
    countdown has actually elapsed (see pomodoroStore.ts), so there's no
    separate "actual time spent" field to track or drift out of sync.
    """
    from django.db.models import Sum

    from poweratomic.pomodoro.models import PomodoroSession

    from .models import UserBadge

    total_seconds = (
        PomodoroSession.objects.filter(
            user=user, phase=PomodoroSession.Phase.WORK, status=PomodoroSession.Status.COMPLETED
        ).aggregate(total=Sum('planned_duration_seconds'))['total']
        or 0
    )
    total_hours = total_seconds / 3600

    earned_keys = set()
    if total_hours >= 5:
        earned_keys.add('focus_bronze')
    if total_hours >= 25:
        earned_keys.add('focus_silver')
    if total_hours >= 100:
        earned_keys.add('focus_gold')

    for key in earned_keys:
        UserBadge.objects.get_or_create(user=user, badge_key=key)