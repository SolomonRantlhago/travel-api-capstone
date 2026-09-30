from rest_framework import serializers
from django.contrib.auth import get_user_model

from .validators import validate_password_strength

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer for project model serializers.
    """
    class Meta:
        abstract = True


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

        # Apply Django's password rules (length, common, numeric, similarity
        # to the username/email) to the not-yet-saved user.
        candidate = User(
            username=data.get('username', ''),
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
        )
        validate_password_strength(data['password'], candidate)
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserProfileSerializer(BaseModelSerializer):
    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['profile_complete'] = all([
            instance.first_name,
            instance.last_name,
            instance.phone,
            instance.date_of_birth,
            instance.bio,
        ])

        return data

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


class AdminUserSerializer(BaseModelSerializer):
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

        validate_password_strength(
            data['new_password'],
            self.context['request'].user,
            field='new_password'
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
