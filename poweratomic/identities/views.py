from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import PRESET_IDENTITIES
from .models import Identity
from .serializers import IdentitySerializer


class PresetIdentitiesView(APIView):
    """GET /api/identities/presets/ - static suggestions for the picker UI."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(PRESET_IDENTITIES)


class IdentityListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/identities/  - the current user's identities (empty list if
                              they haven't picked one yet - the app uses
                              this to decide whether to show the builder)
    POST /api/identities/  - create one, from a preset or custom text
    """

    serializer_class = IdentitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Identity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)