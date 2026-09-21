from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    booked_by_username = serializers.CharField(source='booked_by.username', read_only=True)
    itinerary_title = serializers.CharField(source='itinerary.title', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'itinerary', 'itinerary_title',
            'booked_by', 'booked_by_username', 'reference_number',
            'status', 'payment_status', 'cost', 'currency',
            'booking_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'booked_by', 'created_at', 'updated_at']

    def validate_itinerary(self, value):
        request = self.context.get('request')
        if request and not (request.user.is_staff or request.user.is_superuser):
            if value.owner != request.user:
                raise serializers.ValidationError(
                    "You can only create bookings for your own itineraries."
                )
        return value