from rest_framework import serializers

from destinations.serializers import DestinationSerializer
from travel_api.validators import validate_upload
from .models import (
    Itinerary,
    ItineraryItem,
    ItineraryCollaboration,
)


class ItineraryValidationMixin:
    """
    Validation shared by every serializer that writes an itinerary, so the
    create, update and detail serializers all enforce the same rules.
    """

    def validate_pdf_file(self, value):
        return validate_upload(
            value,
            max_mb=10,
            content_types=['application/pdf'],
            extensions=['.pdf'],
            size_message="PDF file size cannot exceed 10 MB.",
            type_message="Only PDF files are allowed.",
        )

    def validate(self, data):
        """
        End date must not precede the start date. On a partial update
        (PATCH) only one date may be sent, so fall back to the value that is
        already stored on the instance for the other one.
        """
        start_date = data.get(
            'start_date', getattr(self.instance, 'start_date', None)
        )
        end_date = data.get(
            'end_date', getattr(self.instance, 'end_date', None)
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date."}
            )

        return data


class ItineraryItemSerializer(serializers.ModelSerializer):
    destination_detail = DestinationSerializer(
        source='destination',
        read_only=True
    )

    class Meta:
        model = ItineraryItem
        fields = [
            'id',
            'itinerary',
            'destination',
            'destination_detail',
            'day_number',
            'notes',
            'order',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        validators = []
        extra_kwargs = {
            'itinerary': {'write_only': True, 'required': False},
            'destination': {'write_only': True},
        }

    def validate(self, data):
        """
        The automatic unique_together validator is switched off (the
        itinerary comes from the URL, not the body), so enforce
        "one destination per day per itinerary" here - otherwise a
        duplicate would surface as a database error.
        """
        view = self.context.get('view')
        if hasattr(view, 'get_itinerary'):
            itinerary = view.get_itinerary()
        else:
            itinerary = data.get(
                'itinerary', getattr(self.instance, 'itinerary', None)
            )
        destination = data.get(
            'destination', getattr(self.instance, 'destination', None)
        )
        day_number = data.get(
            'day_number', getattr(self.instance, 'day_number', None)
        )

        duplicates = ItineraryItem.objects.filter(
            itinerary=itinerary,
            destination=destination,
            day_number=day_number
        )
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if itinerary and duplicates.exists():
            raise serializers.ValidationError(
                "This destination is already planned for that day."
            )

        return data


class ItinerarySerializer(ItineraryValidationMixin,
                          serializers.ModelSerializer):
    items = ItineraryItemSerializer(
        many=True,
        read_only=True
    )

    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True
    )

    duration_days = serializers.SerializerMethodField()

    def get_duration_days(self, obj) -> int:
        return obj.calculate_duration()

    class Meta:
        model = Itinerary
        fields = [
            'id',
            'title',
            'description',
            'owner',
            'owner_username',
            'start_date',
            'end_date',
            'status',
            'is_public',
            'pdf_file',
            'duration_days',
            'items',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'owner',
            'created_at',
            'updated_at'
        ]


class ItineraryWriteSerializer(ItineraryValidationMixin,
                               serializers.ModelSerializer):
    """
    Base for the create and update serializers: the writable fields plus
    the shared date and PDF validation (DRY).
    """

    class Meta:
        model = Itinerary
        fields = [
            'title',
            'description',
            'start_date',
            'end_date',
            'status',
            'is_public',
            'pdf_file',
        ]


class ItineraryCreateSerializer(ItineraryWriteSerializer):
    """Fields accepted when creating an itinerary."""


class ItineraryUpdateSerializer(ItineraryWriteSerializer):
    """Fields accepted when updating an itinerary."""


class ItineraryListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True
    )

    class Meta:
        model = Itinerary
        fields = [
            'id',
            'title',
            'start_date',
            'end_date',
            'status',
            'is_public',
            'owner_username',
        ]
        read_only_fields = ['id']


class ItineraryCollaborationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = ItineraryCollaboration
        fields = [
            'id',
            'itinerary',
            'user',
            'username',
            'role',
            'created_at',
        ]
        read_only_fields = ['id', 'itinerary', 'username', 'created_at']

    def validate_user(self, value):
        """
        The owner cannot be added as a collaborator, and the same person
        cannot be added twice. (Only checked when adding, not when changing
        a role - see update().)
        """
        if self.instance is not None:
            return value

        view = self.context.get('view')
        itinerary = view.get_itinerary() if view else None

        if itinerary and value == itinerary.owner:
            raise serializers.ValidationError(
                "The owner is already part of this itinerary."
            )

        if itinerary and ItineraryCollaboration.objects.filter(
            itinerary=itinerary, user=value
        ).exists():
            raise serializers.ValidationError(
                "This user is already a collaborator."
            )

        return value

    def create(self, validated_data):
        return ItineraryCollaboration.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Only the role may change - never who the collaborator is."""
        validated_data.pop('user', None)
        instance.role = validated_data.get('role', instance.role)
        instance.save(update_fields=['role'])
        return instance
