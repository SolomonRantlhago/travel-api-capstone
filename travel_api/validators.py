"""Reusable upload validators shared by several serializers."""
import os

from rest_framework import serializers


def validate_upload(value, *, max_mb, content_types, extensions,
                    size_message, type_message):
    """
    Check an uploaded file's size, MIME type and extension.

    Both the declared content type *and* the file extension must be allowed,
    because the content type alone is supplied by the client.
    Returns the file unchanged, or raises a DRF ValidationError.
    """
    if not value:
        return value

    if value.size > max_mb * 1024 * 1024:
        raise serializers.ValidationError(size_message)

    extension = os.path.splitext(value.name)[1].lower()
    content_type = getattr(value, 'content_type', None)

    if extension not in extensions or content_type not in content_types:
        raise serializers.ValidationError(type_message)

    return value
