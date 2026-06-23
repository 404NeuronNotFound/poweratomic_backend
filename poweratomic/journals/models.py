import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class JournalEntry(models.Model):
    """
    Morning: "What vote will you cast for your future self today?"
    Evening: "Did your actions match the person you are becoming?"

    One row per (user, date, entry_type) - unlike a check-in, a journal
    entry is meant to be revisited and edited through the day, so writing
    again doesn't just confirm what's there, it overwrites the content.
    """

    MORNING = 'morning'
    EVENING = 'evening'
    ENTRY_TYPE_CHOICES = [(MORNING, 'Morning'), (EVENING, 'Evening')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='journal_entries', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    entry_type = models.CharField(max_length=7, choices=ENTRY_TYPE_CHOICES)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date', 'entry_type')
        ordering = ['-date', 'entry_type']

    def __str__(self):
        return f'{self.user} - {self.date} - {self.entry_type}'