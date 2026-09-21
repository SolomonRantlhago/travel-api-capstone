from django.contrib import admin
from .models import Itinerary, ItineraryItem


class ItineraryItemInline(admin.TabularInline):
    model = ItineraryItem
    extra = 1


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'start_date', 'end_date', 'status', 'is_public']
    list_filter = ['status', 'is_public']
    search_fields = ['title', 'owner__username']
    inlines = [ItineraryItemInline]


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ['itinerary', 'destination', 'day_number', 'order']
    list_filter = ['itinerary']