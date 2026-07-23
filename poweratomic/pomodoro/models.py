import uuid

from django.conf import settings
from django.db import models

# Matches the actual project layout confirmed from urls.py
# (poweratomic.habits.urls) - the habits app lives under the
# poweratomic package, not as a flat top-level app.
from poweratomic.habits.models import Habit


class PomodoroSettings(models.Model):
    """
    Per-user Pomodoro configuration (work/break durations, cycle cadence).
    Created lazily via get_or_create on first access (see
    PomodoroSettingsView) rather than at signup, since most users may
    never touch the defaults.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pomodoro_settings'
    )
    work_minutes = models.PositiveSmallIntegerField(default=25)
    short_break_minutes = models.PositiveSmallIntegerField(default=5)
    long_break_minutes = models.PositiveSmallIntegerField(default=15)
    cycles_before_long_break = models.PositiveSmallIntegerField(default=4)

    # Used by the "Find a time" calendar feature to bound its free-slot
    # search to reasonable hours (never suggest a 3am study block).
    # Plain 0-23 hour integers, not DateTimeField/TimeField, since this
    # is a daily-recurring local-time preference, not a specific instant.
    day_start_hour = models.PositiveSmallIntegerField(default=7)
    day_end_hour = models.PositiveSmallIntegerField(default=22)

    def __str__(self):
        return f'Pomodoro settings for {self.user}'


class PomodoroSession(models.Model):
    """
    A single work/break phase. Deliberately one row per phase (not one row
    per full 4-cycle round) so partial/abandoned sessions are still
    recorded accurately for stats later in Phase 2.

    started_at/planned_duration_seconds are the source of truth for
    timing - the frontend computes remaining time from these rather than
    trusting an in-memory countdown, since RN timers drift or pause when
    the app is backgrounded. This row just needs to record what was
    planned and when it actually ended.
    """

    class Phase(models.TextChoices):
        WORK = 'work', 'Work'
        SHORT_BREAK = 'short_break', 'Short break'
        LONG_BREAK = 'long_break', 'Long break'

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In progress'
        COMPLETED = 'completed', 'Completed'
        ABANDONED = 'abandoned', 'Abandoned'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pomodoro_sessions'
    )
    # Nullable + SET_NULL: a standalone (non-habit-linked) session is
    # valid, and if a habit is later deleted, its past Pomodoro history
    # shouldn't be deleted along with it - just unlinked.
    habit = models.ForeignKey(
        Habit, on_delete=models.SET_NULL, null=True, blank=True, related_name='pomodoro_sessions'
    )

    phase = models.CharField(max_length=20, choices=Phase.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    cycle_number = models.PositiveSmallIntegerField(default=1)

    planned_duration_seconds = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'started_at']),
        ]

    def __str__(self):
        return f'{self.get_phase_display()} ({self.status}) - {self.user}'