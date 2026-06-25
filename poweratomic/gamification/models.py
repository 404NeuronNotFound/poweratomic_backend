import uuid

from django.conf import settings
from django.db import models


class UserXP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='xp_profile', on_delete=models.CASCADE)
    total_xp = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user} - {self.total_xp} XP'
    
class UserBadge(models.Model):
    """
    A record that a badge was earned - the badge catalog itself (name,
    description, what unlocks it) lives in badges.py as a static list,
    not a model, since it never changes per-user. Unlike UserXP, there's
    no signal that ever deletes one of these - badges are permanent once
    earned, even if the streak that earned them later breaks.
    """
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='badges', on_delete=models.CASCADE)
    badge_key = models.CharField(max_length=50)
    earned_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        unique_together = ('user', 'badge_key')
 
    def __str__(self):
        return f'{self.user} - {self.badge_key}'