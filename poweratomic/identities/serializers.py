from rest_framework import serializers

from .models import Identity


class IdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Identity
        fields = ('id', 'label', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_label(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Identity cannot be empty.')
        return value