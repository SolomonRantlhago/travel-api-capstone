from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'itinerary', 'booked_by', 'status',
                     'payment_status', 'cost', 'currency', 'booking_date']
    list_filter = ['status', 'payment_status', 'currency']
    search_fields = ['reference_number', 'itinerary__title', 'booked_by__username']