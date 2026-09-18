from rest_framework import serializers
from .models import Destination


class DestinationSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'country', 'city', 'description', 'category',
            'price_range', 'image', 'latitude', 'longitude', 'best_season',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']