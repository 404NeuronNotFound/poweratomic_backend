from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from poweratomic.habits.models import Habit

from .models import DailyCheckIn
from .serializers import DailyCheckInSerializer
from .services import compute_habit_stats


class TodayCheckInsView(APIView):
    """GET /api/checkins/today/ - which of the user's habits are done today."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        checkins = DailyCheckIn.objects.filter(user=request.user, date=today)
        return Response(DailyCheckInSerializer(checkins, many=True).data)


class CheckInCreateView(generics.CreateAPIView):
    """POST /api/checkins/ - mark a habit done for today. {"habit": "<id>", "note": "optional"}"""

    serializer_class = DailyCheckInSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckInDeleteView(generics.DestroyAPIView):
    """DELETE /api/checkins/<id>/ - undo today's check-in (misclicks happen)."""

    serializer_class = DailyCheckInSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Scoping to the current user here means a mismatched id 404s
        # instead of leaking whether it exists for someone else.
        return DailyCheckIn.objects.filter(user=self.request.user)
    
class DashboardView(APIView):
    """
    GET /api/checkins/dashboard/ - today's completion, a rolling 7-day
    trend, and all-time totals, all in one call so the dashboard screen
    doesn't need to stitch together several requests itself.
 
    "Total" in today/weekly always means CURRENTLY active habits - this
    reflects your present routine, not deprecated ones. "Total check-ins"
    in all-time, by contrast, counts every check-in ever logged regardless
    of whether its habit is still active - archiving a habit shouldn't
    shrink your lifetime total.
    """
 
    permission_classes = [permissions.IsAuthenticated]
 
    def get(self, request):
        user = request.user
        today = timezone.localdate()
 
        active_count = Habit.objects.filter(user=user, is_active=True).count()
 
        def completed_on(d):
            return DailyCheckIn.objects.filter(user=user, date=d, habit__is_active=True).count()
 
        # Oldest to newest, 6 days ago through today - a rolling window,
        # not calendar-week-aligned, since "this week" for a personal
        # dashboard reads more naturally as "the last 7 days."
        weekly = [
            {
                'date': (today - timedelta(days=offset)).isoformat(),
                'completed': completed_on(today - timedelta(days=offset)),
                'total': active_count,
            }
            for offset in range(6, -1, -1)
        ]
 
        total_checkins = DailyCheckIn.objects.filter(user=user).count()
        # Best streak ever, across ALL habits including archived ones -
        # a personal record shouldn't disappear just because you stopped
        # tracking that habit.
        best_streak = max(
            (compute_habit_stats(h)['longest_streak'] for h in Habit.objects.filter(user=user)),
            default=0,
        )
 
        return Response({
            'today': {'completed': completed_on(today), 'total': active_count},
            'weekly': weekly,
            'totals': {
                'active_habits': active_count,
                'total_checkins': total_checkins,
                'best_streak': best_streak,
            },
        })
 