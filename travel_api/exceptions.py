"""Project-wide DRF exception handler."""
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback


def custom_exception_handler(exc, context):
    """
    Extend DRF's default handler so that errors raised by Django itself
    are returned as clean JSON instead of crashing with a 500:

    * django ValidationError -> 400 Bad Request
    * IntegrityError         -> 409 Conflict

    Everything else (401, 403, 404, DRF validation errors...) is handled
    by DRF's default handler and keeps its usual shape.
    """
    if isinstance(exc, DjangoValidationError):
        set_rollback()
        return Response(
            {'detail': exc.messages},
            status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, IntegrityError):
        set_rollback()
        return Response(
            {'detail': 'This change conflicts with existing data.'},
            status=status.HTTP_409_CONFLICT
        )

    return exception_handler(exc, context)
