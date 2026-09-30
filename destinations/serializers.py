from rest_framework import serializers

from travel_api.validators import validate_upload
from .models import Destination, Amenity, DestinationAmenity


class ImageUploadValidationMixin:
    """
    Size (5 MB) and type (JPEG/PNG/WebP) checks for a destination image.
    Shared by every serializer that accepts an `image` upload so the
    rules cannot be bypassed by using the create/update serializers.
    """

    def validate_image(self, value):
        return validate_upload(
            value,
            max_mb=5,
            content_types=['image/jpeg', 'image/png', 'image/webp'],
            extensions=['.jpg', '.jpeg', '.png', '.webp'],
            size_message="Image file size cannot exceed 5 MB.",
            type_message="Only JPEG, PNG, and WebP images are allowed.",
        )


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


class DestinationSerializer(ImageUploadValidationMixin,
                            serializers.ModelSerializer):

    name = serializers.CharField(
        help_text="Name of the travel destination."
    )

    country = serializers.CharField(
        help_text="Country where the destination is located."
    )

    city = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="City where the destination is located."
    )

    description = serializers.CharField(
        help_text="Description of the destination."
    )

    category = serializers.ChoiceField(
        choices=Destination.CATEGORY_CHOICES,
        help_text="Type of destination, such as beach, mountain, or city."
    )

    price_range = serializers.ChoiceField(
        choices=Destination.PRICE_RANGE_CHOICES,
        help_text="Expected price range for the destination."
    )

    image = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Destination image. Maximum file size is 5 MB."
    )

    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        help_text="Latitude coordinate of the destination."
    )

    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        help_text="Longitude coordinate of the destination."
    )

    best_season = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Best season or time of year to visit."
    )

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

    def get_full_location(self, obj) -> str:
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


class DestinationWriteSerializer(ImageUploadValidationMixin,
                                 serializers.ModelSerializer):
    """
    Base for the create and update serializers: the writable fields and
    the shared image validation live here (DRY).
    """

    class Meta:
        model = Destination
        fields = [
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
        ]


class DestinationCreateSerializer(DestinationWriteSerializer):
    """Fields accepted when creating a destination."""


class DestinationUpdateSerializer(DestinationWriteSerializer):
    """Fields accepted when updating a destination."""


class DestinationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = [
            'id',
            'name',
            'country',
            'city',
            'category',
            'price_range',
            'image',
        ]
        read_only_fields = ['id']
