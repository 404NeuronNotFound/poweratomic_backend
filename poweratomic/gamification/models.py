from django.conf import settings
from django.db import models


class UserXP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='xp_profile', on_delete=models.CASCADE)
    total_xp = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user} - {self.total_xp} XP'