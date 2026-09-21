from rest_framework import serializers
from .models import Itinerary, ItineraryItem
from destinations.serializers import DestinationSerializer


class ItineraryItemSerializer(serializers.ModelSerializer):
    destination_detail = DestinationSerializer(source='destination', read_only=True)

    class Meta:
        model = ItineraryItem
        fields = ['id', 'itinerary', 'destination', 'destination_detail',
                  'day_number', 'notes', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
        validators = []
        extra_kwargs = {
            'itinerary': {'write_only': True, 'required': False},
            'destination': {'write_only': True},
        }


class ItinerarySerializer(serializers.ModelSerializer):
    items = ItineraryItemSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Itinerary
        fields = ['id', 'title', 'description', 'owner', 'owner_username',
                  'start_date', 'end_date', 'status', 'is_public',
                  'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']