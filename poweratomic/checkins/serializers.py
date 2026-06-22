from django.utils import timezone
from rest_framework import serializers

from poweratomic.habits.models import Habit

from .models import DailyCheckIn


class DailyCheckInSerializer(serializers.ModelSerializer):
    habit = serializers.PrimaryKeyRelatedField(queryset=Habit.objects.all())
    habit_title = serializers.CharField(source='habit.title', read_only=True)

    class Meta:
        model = DailyCheckIn
        fields = ('id', 'habit', 'habit_title', 'date', 'note', 'created_at')
        # date is never client-supplied - "did I do this today" only ever
        # means the server's today, not whatever the device clock says
        read_only_fields = ('id', 'date', 'created_at')
        # DRF auto-generates a UniqueTogetherValidator for the (habit, date)
        # constraint, which runs during is_valid() and would reject a
        # second check-in with a validation error - before create() ever
        # gets a chance to make this idempotent via get_or_create. We want
        # the second tap to just confirm what's already there, not error.
        validators = []

    def validate_habit(self, value):
        request = self.context['request']
        if value.user_id != request.user.id:
            raise serializers.ValidationError("That habit doesn't belong to you.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        # Idempotent on purpose: tapping "done" twice (double-tap, retry
        # after a flaky connection) should not error, just return the
        # existing check-in for today.
        checkin, _ = DailyCheckIn.objects.get_or_create(
            habit=validated_data['habit'],
            date=timezone.localdate(),
            defaults={'user': user, 'note': validated_data.get('note', '')},
        )
        return checkin