"""Validators used by the account serializers and views."""
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


def validate_password_strength(password, user=None, field='password'):
    """
    Run Django's AUTH_PASSWORD_VALIDATORS and turn any failure into a
    DRF ValidationError, so the API answers 400 instead of crashing.
    """
    try:
        password_validation.validate_password(password, user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError({field: list(exc.messages)})
