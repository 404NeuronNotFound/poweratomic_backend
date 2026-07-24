from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PomodoroSession, PomodoroSettings
from .serializers import (
    PomodoroSessionCreateSerializer,
    PomodoroSessionSerializer,
    PomodoroSettingsSerializer,
)
from .services import create_habit_checkin


class PomodoroSettingsView(generics.RetrieveUpdateAPIView):
    """GET/PATCH the current user's Pomodoro durations & cycle cadence.
    get_or_create means a user never needs an explicit "initialize
    settings" step - defaults apply until they change something."""

    serializer_class = PomodoroSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = PomodoroSettings.objects.get_or_create(user=self.request.user)
        return obj


class PomodoroSessionListCreateView(generics.ListCreateAPIView):
    """GET: this user's session history (most recent first, via model
    Meta.ordering). POST: start a new session."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PomodoroSession.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return PomodoroSessionCreateSerializer if self.request.method == 'POST' else PomodoroSessionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Respond with the full read serializer (habit_title etc.) rather
        # than the create serializer's narrower field set, so the
        # frontend gets back everything it needs in one round trip.
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        self.perform_create(create_serializer)

        read_serializer = PomodoroSessionSerializer(create_serializer.instance)
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PomodoroSessionCompleteView(APIView):
    """
    Marks a session as completed. If it was a WORK phase tied to a habit,
    also attempts to create today's check-in for that habit.

    The check-in bridge is currently a stub (see services.py) - this view
    is written so wiring it up later is a one-line change in services.py,
    with no changes needed here.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            session = PomodoroSession.objects.get(pk=pk, user=request.user)
        except PomodoroSession.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        session.status = PomodoroSession.Status.COMPLETED
        session.completed_at = timezone.now()
        session.save(update_fields=['status', 'completed_at'])

        checkin_created = None
        if session.phase == PomodoroSession.Phase.WORK and session.habit_id:
            # Best-effort: a failure or stub result here should never
            # block the session itself from being marked complete.
            checkin_created = create_habit_checkin(request.user, session.habit)

        data = PomodoroSessionSerializer(session).data
        data['checkin_created'] = checkin_created
        return Response(data)


class PomodoroSessionAbandonView(APIView):
    """Marks a session as abandoned (user backed out early) rather than
    deleting it - abandoned sessions still matter for honest stats later
    (e.g. completion rate), same spirit as how habits track completion_rate."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            session = PomodoroSession.objects.get(pk=pk, user=request.user)
        except PomodoroSession.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        session.status = PomodoroSession.Status.ABANDONED
        session.completed_at = timezone.now()
        session.save(update_fields=['status', 'completed_at'])
        return Response(PomodoroSessionSerializer(session).data)


class PomodoroStatsView(APIView):
    """
    Aggregates completed WORK-phase sessions two ways:
    - daily: totals for the last 30 days, for a mini-calendar heatmap.
    - by_habit: all-time totals per linked habit, for a "which habits get
      the most focus time" breakdown.

    Only phase=WORK, status=COMPLETED sessions count - breaks aren't
    "focus time", and abandoned sessions didn't actually happen for the
    full planned duration, so counting planned_duration_seconds only for
    completed sessions is accurate (no need to track actual elapsed time
    separately).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        completed_work = PomodoroSession.objects.filter(
            user=request.user,
            phase=PomodoroSession.Phase.WORK,
            status=PomodoroSession.Status.COMPLETED,
        )

        window_start = timezone.now() - timedelta(days=30)
        daily_qs = (
            completed_work.filter(started_at__gte=window_start)
            .annotate(day=TruncDate('started_at'))
            .values('day')
            .annotate(seconds=Sum('planned_duration_seconds'))
            .order_by('day')
        )
        daily = [
            {'date': row['day'].isoformat(), 'minutes': round(row['seconds'] / 60)}
            for row in daily_qs
        ]

        # All-time, not windowed to a year - "which habits get the most
        # focus time" is more useful as a lifetime picture than one that
        # quietly drops older sessions.
        by_habit_qs = (
            completed_work.filter(habit__isnull=False)
            .values('habit_id', 'habit__title')
            .annotate(seconds=Sum('planned_duration_seconds'))
            .order_by('-seconds')
        )
        by_habit = [
            {
                'habit_id': str(row['habit_id']),
                'habit_title': row['habit__title'],
                'minutes': round(row['seconds'] / 60),
            }
            for row in by_habit_qs
        ]

        # "Usual focus hour" - the most frequent hour-of-day (0-23) a
        # work session started, over the last 60 days. Used by the
        # frontend's time-of-day smart nudge ("you usually focus around
        # now"). 60 days (not all-time) so this stays responsive to a
        # genuinely changed routine rather than being anchored to
        # whatever someone's schedule looked like a year ago.
        #
        # CAVEAT: __hour lookups on a DateTimeField are evaluated in
        # Django's configured TIME_ZONE (a single server-wide setting),
        # not the individual user's device timezone, which isn't stored
        # per-session. For a single-timezone user base this is fine; if
        # users span timezones or travel, this can be off. Flagging
        # rather than silently getting it wrong - fixing this properly
        # would mean storing each session's originating timezone, which
        # isn't currently captured anywhere.
        sixty_days_ago = timezone.now() - timedelta(days=60)
        hour_counts = (
            completed_work.filter(started_at__gte=sixty_days_ago)
            .values('started_at__hour')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        usual_hour = hour_counts[0]['started_at__hour'] if hour_counts else None

        return Response({'daily': daily, 'by_habit': by_habit, 'usual_hour': usual_hour})