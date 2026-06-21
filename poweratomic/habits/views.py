from rest_framework import generics, permissions

from .models import Habit
from .serializers import HabitSerializer


class HabitListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/habits/  - the current user's habits, with their laws nested
    POST /api/habits/  - create a habit + its four laws in one request
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).select_related('law', 'identity')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)