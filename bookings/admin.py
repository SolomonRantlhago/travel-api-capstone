from django.contrib import admin
from .models import Booking, Accommodation, Activity, ActivityLog


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "destination",
        "accommodation_type",
        "price_per_night",
        "is_available",
    ]
    list_filter = ["accommodation_type", "is_available"]
    search_fields = ["name", "destination__name", "address"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "destination",
        "category",
        "price",
        "duration_hours",
        "is_available",
    ]
    list_filter = ["category", "is_available"]
    search_fields = ["name", "destination__name"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "reference_number",
        "itinerary",
        "booked_by",
        "accommodation",
        "activity",
        "status",
        "payment_status",
        "cost",
        "currency",
        "booking_date",
    ]
    list_filter = ["status", "payment_status", "currency"]
    search_fields = [
        "reference_number",
        "itinerary__title",
        "booked_by__username",
    ]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "user",
        "action",
        "entity_type",
        "entity_id",
        "description",
    ]
    list_filter = ["action", "entity_type"]
    search_fields = ["description", "user__username"]
    readonly_fields = [
        "user",
        "action",
        "entity_type",
        "entity_id",
        "description",
        "metadata",
        "ip_address",
        "created_at",
    ]
