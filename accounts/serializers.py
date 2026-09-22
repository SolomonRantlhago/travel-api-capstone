from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name'
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'date_of_birth',
            'bio',
            'profile_picture',
            'travel_preferences',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'created_at'
        ]


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'date_of_birth',
            'bio',
            'profile_picture',
            'travel_preferences',
            'is_active',
            'is_staff',
            'is_superuser',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'created_at'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your current password is incorrect."
            )

        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"new_password": "Passwords do not match."}
            )

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"new_password": "Passwords do not match."}
            )

        return data