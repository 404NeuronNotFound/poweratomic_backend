from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailyCheckIn
from .serializers import DailyCheckInSerializer


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