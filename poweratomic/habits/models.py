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
    
class HabitStack(models.Model):
    """
    A named, ordered routine - "Wake Up -> Drink Water -> Read Notes ->
    Study" - made up of habits that already exist. Purely organizational:
    a stack has no completion or scoring logic of its own. Each habit
    inside it still checks in independently exactly as it already does;
    this is just a way to group and sequence them.
    """
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='habit_stacks', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['created_at']
 
    def __str__(self):
        return f'{self.name} ({self.user})'
 
 
class HabitStackItem(models.Model):
    """One habit's position within a stack. The same habit can appear in
    several different stacks - just not twice in the same one."""
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stack = models.ForeignKey(HabitStack, related_name='items', on_delete=models.CASCADE)
    habit = models.ForeignKey(Habit, related_name='stack_items', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
 
    class Meta:
        ordering = ['order']
        unique_together = ('stack', 'habit')
 
    def __str__(self):
        return f'{self.stack.name} #{self.order}: {self.habit.title}'