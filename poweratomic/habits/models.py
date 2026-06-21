import uuid

from django.conf import settings
from django.db import models

from poweratomic.identities.models import Identity


class Habit(models.Model):
    GOOD = 'good'
    BAD = 'bad'
    HABIT_TYPE_CHOICES = [(GOOD, 'Good'), (BAD, 'Bad')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='habits', on_delete=models.CASCADE)
    # Nullable: a habit doesn't strictly require an identity, but the
    # builder UI encourages picking one - "Identity First" from the white
    # paper. SET_NULL so deleting an Identity later doesn't take its
    # habits down with it.
    identity = models.ForeignKey(
        Identity, related_name='habits', on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=100)
    # Only "good" habit creation is built this chunk - the field exists now
    # so bad-habit elimination (later) can reuse this model instead of a
    # parallel one, per the white paper's plan.
    habit_type = models.CharField(max_length=4, choices=HABIT_TYPE_CHOICES, default=GOOD)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.user})'


class HabitLaw(models.Model):
    """
    The Four Laws of Behavior Change, one set per Habit. For a `good`
    habit these read literally (Make It Obvious/Attractive/Easy/
    Satisfying). Bad-habit elimination (built later) reuses the exact same
    four fields with inverted meaning - habit.habit_type decides how the
    app *labels* them, the storage shape doesn't need to change.
    """

    habit = models.OneToOneField(Habit, related_name='law', on_delete=models.CASCADE)

    cue = models.CharField(max_length=150, blank=True)              # Make It Obvious - trigger
    time = models.CharField(max_length=50, blank=True)               # Make It Obvious - when
    location = models.CharField(max_length=100, blank=True)          # Make It Obvious - where
    reward = models.CharField(max_length=150, blank=True)             # Make It Attractive
    minimum_action = models.CharField(max_length=150, blank=True)    # Make It Easy
    satisfaction_note = models.CharField(max_length=150, blank=True)  # Make It Satisfying

    def __str__(self):
        return f'Laws for {self.habit.title}'