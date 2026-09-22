from rest_framework import serializers
from .models import Destination, Amenity, DestinationAmenity


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class DestinationAmenitySerializer(serializers.ModelSerializer):
    amenity_detail = AmenitySerializer(
        source='amenity',
        read_only=True
    )

    class Meta:
        model = DestinationAmenity
        fields = [
            'id',
            'amenity',
            'amenity_detail',
            'is_free',
            'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DestinationSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )

    amenities = DestinationAmenitySerializer(
        source='destination_amenities',
        many=True,
        read_only=True
    )

    full_location = serializers.SerializerMethodField()

    def get_full_location(self, obj):
        return obj.get_full_location()

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Destination name cannot be blank."
            )

        return value.strip()

    class Meta:
        model = Destination
        fields = [
            'id',
            'name',
            'country',
            'city',
            'description',
            'category',
            'price_range',
            'image',
            'latitude',
            'longitude',
            'best_season',
            'created_by',
            'created_by_username',
            'full_location',
            'amenities',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at'
        ]