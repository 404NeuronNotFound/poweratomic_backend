from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserXP
from .serializers import UserXPSerializer


class ProgressView(APIView):
    """GET /api/progress/ - current user's XP total, level, and progress toward the next one."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = UserXP.objects.get_or_create(user=request.user)
        return Response(UserXPSerializer(profile).data)