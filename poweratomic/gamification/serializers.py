from rest_framework import serializers

from .levels import level_for_xp


class UserXPSerializer(serializers.Serializer):
    total_xp = serializers.IntegerField()
    level = serializers.SerializerMethodField()
    xp_into_level = serializers.SerializerMethodField()
    xp_for_next_level = serializers.SerializerMethodField()

    def get_level(self, obj):
        name, _, _ = level_for_xp(obj.total_xp)
        return name

    def get_xp_into_level(self, obj):
        _, into, _ = level_for_xp(obj.total_xp)
        return into

    def get_xp_for_next_level(self, obj):
        _, _, for_next = level_for_xp(obj.total_xp)
        return for_next