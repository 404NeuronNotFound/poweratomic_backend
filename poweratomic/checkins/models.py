import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from poweratomic.habits.models import Habit


class DailyCheckIn(models.Model):
    """
    "Did you do this today?" - one row per habit per day. The unique
    constraint on (habit, date) is the real guard here, not just app-level
    logic: even a buggy or duplicate request can't create two check-ins
    for the same habit on the same day.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='checkins', on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, related_name='checkins', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.habit.title} - {self.date}'