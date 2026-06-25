from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from poweratomic.checkins.models import DailyCheckIn
from poweratomic.gamification.badges import check_and_award_badges

from .models import UserXP

XP_PER_CHECKIN = 10


@receiver(post_save, sender=DailyCheckIn)
def award_xp_on_checkin(sender, instance, created, **kwargs):
    if not created:
        return
    profile, _ = UserXP.objects.get_or_create(user=instance.user)
    profile.total_xp += XP_PER_CHECKIN
    profile.save(update_fields=['total_xp'])


@receiver(post_delete, sender=DailyCheckIn)
def remove_xp_on_checkin_delete(sender, instance, **kwargs):
    profile, _ = UserXP.objects.get_or_create(user=instance.user)
    profile.total_xp = max(0, profile.total_xp - XP_PER_CHECKIN)
    profile.save(update_fields=['total_xp'])

@receiver(post_save, sender=DailyCheckIn)
def check_badges_on_checkin(sender, instance, created, **kwargs):
    if not created:
        return
    # Deliberately no matching post_delete handler - badges earned stay
    # earned even if the streak that earned them later breaks.
    check_and_award_badges(instance.user)
 