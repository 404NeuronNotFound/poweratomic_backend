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