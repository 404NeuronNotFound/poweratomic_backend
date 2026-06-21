from rest_framework import serializers

from poweratomic.identities.models import Identity

from .models import Habit, HabitLaw


class HabitLawSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLaw
        fields = ('cue', 'time', 'location', 'reward', 'minimum_action', 'satisfaction_note')


class HabitSerializer(serializers.ModelSerializer):
    law = HabitLawSerializer()
    identity = serializers.PrimaryKeyRelatedField(
        queryset=Identity.objects.all(), required=False, allow_null=True
    )
    identity_label = serializers.CharField(source='identity.label', read_only=True, default=None)

    class Meta:
        model = Habit
        fields = (
            'id',
            'title',
            'habit_type',
            'identity',
            'identity_label',
            'is_active',
            'created_at',
            'law',
        )
        read_only_fields = ('id', 'created_at')

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Habit title cannot be empty.')
        return value

    def validate_identity(self, value):
        # Without this, a user could pass another user's Identity id and
        # link a habit to it - PrimaryKeyRelatedField only checks the id
        # exists, not who it belongs to.
        request = self.context['request']
        if value is not None and value.user_id != request.user.id:
            raise serializers.ValidationError("That identity doesn't belong to you.")
        return value

    def create(self, validated_data):
        law_data = validated_data.pop('law')
        habit = Habit.objects.create(**validated_data)
        HabitLaw.objects.create(habit=habit, **law_data)
        return habit