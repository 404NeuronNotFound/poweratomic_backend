from rest_framework import generics, permissions

from .models import Habit, HabitStack
from .serializers import HabitSerializer, HabitStackSerializer


class HabitListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/habits/  - the current user's ACTIVE habits, with laws nested.
                          Archived (is_active=False) habits are excluded -
                          they're not gone, just hidden from the main list.
    POST /api/habits/  - create a habit + its four laws in one request
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Habit.objects.filter(user=self.request.user, is_active=True)
            .select_related('law', 'identity')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/habits/<id>/  - a single habit (active OR archived - this
                                 is how a previously-archived one gets
                                 reactivated: GET it, then PATCH it)
    PATCH  /api/habits/<id>/  - partial update, including the nested law
    DELETE /api/habits/<id>/  - ARCHIVES, does not actually delete. A real
                                 delete would cascade and wipe the habit's
                                 check-in history, which is exactly the
                                 streak/XP/badge data worth keeping.
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Intentionally NOT filtered by is_active - this view needs to
        # reach an archived habit too, for both reactivation and for
        # simply viewing it.
        return Habit.objects.filter(user=self.request.user).select_related('law', 'identity')

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class HabitStackListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/habits/stacks/  - the current user's routines, items nested and ordered
    POST /api/habits/stacks/  - create a routine + its ordered items in one request
    """
 
    serializer_class = HabitStackSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_queryset(self):
        return HabitStack.objects.filter(user=self.request.user).prefetch_related('items__habit')
 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
 
 
class HabitStackDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH  /api/habits/stacks/<id>/  - rename and/or replace the item set
    DELETE /api/habits/stacks/<id>/  - a REAL delete, unlike Habit - a
                                        stack has no check-in history of
                                        its own to lose; the habits inside
                                        it are untouched.
    """
 
    serializer_class = HabitStackSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def get_queryset(self):
        return HabitStack.objects.filter(user=self.request.user).prefetch_related('items__habit')
 