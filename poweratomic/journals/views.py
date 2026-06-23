from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JournalEntry
from .serializers import JournalEntrySerializer


class TodayJournalView(APIView):
    """
    GET /api/journal/today/ - {"morning": {...} | null, "evening": {...} | null}
    Shaped as an object rather than a list since the app always wants both
    slots specifically, not an arbitrary collection.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        entries = JournalEntry.objects.filter(user=request.user, date=today)
        by_type = {e.entry_type: JournalEntrySerializer(e).data for e in entries}
        return Response({
            'morning': by_type.get(JournalEntry.MORNING),
            'evening': by_type.get(JournalEntry.EVENING),
        })


class JournalHistoryView(generics.ListAPIView):
    """GET /api/journal/history/ - past entries, most recent first."""

    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)


class JournalWriteView(generics.CreateAPIView):
    """POST /api/journal/ - {"entry_type": "morning"|"evening", "content": "..."} - upserts today's entry."""

    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated]