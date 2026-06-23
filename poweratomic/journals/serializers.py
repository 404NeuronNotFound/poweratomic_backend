from django.utils import timezone
from rest_framework import serializers

from .models import JournalEntry


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ('id', 'date', 'entry_type', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'date', 'created_at', 'updated_at')
        # Same reason as DailyCheckIn: DRF's auto unique-together validator
        # would reject a second write instead of letting update_or_create
        # below treat it as an edit.
        validators = []

    def create(self, validated_data):
        user = self.context['request'].user
        entry, _ = JournalEntry.objects.update_or_create(
            user=user,
            date=timezone.localdate(),
            entry_type=validated_data['entry_type'],
            defaults={'content': validated_data.get('content', '')},
        )
        return entry