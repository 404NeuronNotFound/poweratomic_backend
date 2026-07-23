from rest_framework import serializers

from .models import PomodoroSession, PomodoroSettings


class PomodoroSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomodoroSettings
        fields = [
            'work_minutes', 'short_break_minutes', 'long_break_minutes', 'cycles_before_long_break',
            'day_start_hour', 'day_end_hour',
        ]

    def validate(self, data):
        start = data.get('day_start_hour', getattr(self.instance, 'day_start_hour', None))
        end = data.get('day_end_hour', getattr(self.instance, 'day_end_hour', None))
        if start is not None and end is not None and start >= end:
            raise serializers.ValidationError('day_start_hour must be earlier than day_end_hour.')
        return data


class PomodoroSessionSerializer(serializers.ModelSerializer):
    """Read/list shape - includes a denormalized habit_title so the
    frontend doesn't need a second lookup just to render a session card."""

    habit_title = serializers.CharField(source='habit.title', read_only=True, default=None)

    class Meta:
        model = PomodoroSession
        fields = [
            'id', 'habit', 'habit_title', 'phase', 'status', 'cycle_number',
            'planned_duration_seconds', 'started_at', 'completed_at',
        ]
        read_only_fields = ['id', 'started_at']


class PomodoroSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomodoroSession
        fields = ['habit', 'phase', 'cycle_number', 'planned_duration_seconds']

    def validate_habit(self, habit):
        # Prevents linking a session to another user's habit via a guessed
        # UUID - the queryset on the FK field isn't scoped by itself.
        # ASSUMPTION: Habit's owner field is named `user` (habit.user_id).
        # If habits/models.py calls it something else (e.g. `owner`),
        # update this one line.
        if habit is not None:
            request = self.context['request']
            if habit.user_id != request.user.id:
                raise serializers.ValidationError('This habit does not belong to you.')
        return habit