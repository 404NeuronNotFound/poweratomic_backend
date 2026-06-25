from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from poweratomic.gamification.badges import BADGES

from .models import UserBadge, UserXP
from .serializers import UserXPSerializer


class ProgressView(APIView):
    """GET /api/progress/ - current user's XP total, level, and progress toward the next one."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserXP.objects.get_or_create(user=request.user)
        return Response(UserXPSerializer(profile).data)

class BadgeListView(APIView):
    """
    GET /api/progress/badges/ - the full catalog, each entry marked with
    whether this user has earned it (and when). Unearned badges are
    included on purpose, not filtered out - the app shows them locked.
    """
 
    permission_classes = [permissions.IsAuthenticated]
 
    def get(self, request):
        earned = {b.badge_key: b.earned_at for b in UserBadge.objects.filter(user=request.user)}
        data = [
            {
                **badge,
                'earned': badge['key'] in earned,
                'earned_at': earned.get(badge['key']),
            }
            for badge in BADGES
        ]
        return Response(data)