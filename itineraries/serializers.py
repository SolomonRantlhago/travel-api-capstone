from rest_framework import serializers
from .models import Itinerary, ItineraryItem
from destinations.serializers import DestinationSerializer


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


class ItinerarySerializer(serializers.ModelSerializer):
    items = ItineraryItemSerializer(
        many=True,
        read_only=True
    )

    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True
    )

    duration_days = serializers.SerializerMethodField()

    def get_duration_days(self, obj):
        return obj.calculate_duration()

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be before start date."
            )

        return data

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