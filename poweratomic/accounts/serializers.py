from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Validates incoming registration data and creates the user."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'display_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hashes it - never store raw passwords
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of the logged-in user."""

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'display_name', 'created_at')
        read_only_fields = fields


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    PATCH-only fields for editing your own profile. Email and username
    both already carry unique=True on the model (email explicitly,
    username via Django's AbstractUser), so DRF auto-generates the
    uniqueness check - and since this serializer is instantiated with
    `instance=request.user`, that check correctly excludes the user's own
    current value rather than rejecting "no change."
    """

    class Meta:
        model = User
        fields = ('email', 'username', 'display_name')

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Username cannot be empty.')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': "Passwords don't match."})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user