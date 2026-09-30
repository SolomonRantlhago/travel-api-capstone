from rest_framework import serializers
from .models import Booking, Accommodation, Activity, ActivityLog


class AccommodationSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(
        source='destination.name',
        read_only=True
    )

    class Meta:
        model = Accommodation
        fields = [
            'id',
            'name',
            'destination',
            'destination_name',
            'accommodation_type',
            'description',
            'price_per_night',
            'max_guests',
            'amenities',
            'address',
            'contact_email',
            'contact_phone',
            'image',
            'is_available',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ActivitySerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(
        source='destination.name',
        read_only=True
    )

    class Meta:
        model = Activity
        fields = [
            'id',
            'name',
            'destination',
            'destination_name',
            'category',
            'description',
            'duration_hours',
            'price',
            'max_participants',
            'requirements',
            'image',
            'is_available',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    booked_by_username = serializers.CharField(
        source='booked_by.username',
        read_only=True
    )
    itinerary_title = serializers.CharField(
        source='itinerary.title',
        read_only=True
    )
    accommodation_detail = AccommodationSerializer(
        source='accommodation',
        read_only=True
    )
    activity_detail = ActivitySerializer(
        source='activity',
        read_only=True
    )
    is_active = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['booking_summary'] = (
            f"{instance.reference_number} - "
            f"{instance.status} - "
            f"{instance.payment_status}"
        )
        return data

    def get_is_active(self, obj) -> bool:
        return obj.is_active()

    def validate(self, data):
        accommodation = data.get(
            'accommodation',
            getattr(self.instance, 'accommodation', None)
        )
        activity = data.get(
            'activity',
            getattr(self.instance, 'activity', None)
        )
        if accommodation and activity:
            raise serializers.ValidationError(
                'Booking cannot have both accommodation and activity.'
            )
        check_in = data.get(
            'check_in',
            getattr(self.instance, 'check_in', None)
        )
        check_out = data.get(
            'check_out',
            getattr(self.instance, 'check_out', None)
        )
        if check_in and check_out and check_out < check_in:
            raise serializers.ValidationError(
                {'check_out': 'Check-out must be on or after check-in.'}
            )
        return data

    class Meta:
        model = Booking
        fields = [
            'id',
            'itinerary',
            'itinerary_title',
            'booked_by',
            'booked_by_username',
            'accommodation',
            'accommodation_detail',
            'activity',
            'activity_detail',
            'reference_number',
            'status',
            'is_active',
            'payment_status',
            'cost',
            'currency',
            'booking_date',
            'check_in',
            'check_out',
            'guests_count',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'booked_by',
            'created_at',
            'updated_at',
        ]

    def validate_itinerary(self, value):
        request = self.context.get('request')
        if request and not (
            request.user.is_staff or request.user.is_superuser
            or getattr(request.user, 'is_site_admin', False)
        ):
            if value.owner != request.user:
                raise serializers.ValidationError(
                    'You can only create bookings for your own itineraries.'
                )
        return value


class BookingListSerializer(serializers.ModelSerializer):
    itinerary_title = serializers.CharField(
        source='itinerary.title',
        read_only=True
    )
    booked_by_username = serializers.CharField(
        source='booked_by.username',
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'itinerary_title',
            'booked_by_username',
            'reference_number',
            'status',
            'payment_status',
            'cost',
            'currency',
            'booking_date',
            'accommodation',
            'activity',
        ]
        read_only_fields = ['id']


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True,
        default=None
    )

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'user',
            'username',
            'action',
            'entity_type',
            'entity_id',
            'description',
            'metadata',
            'ip_address',
            'created_at',
        ]
        read_only_fields = fields
