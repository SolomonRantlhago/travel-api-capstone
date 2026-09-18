from django.contrib import admin
from .models import Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'category', 'price_range', 'created_by', 'created_at']
    list_filter = ['category', 'price_range', 'country']
    search_fields = ['name', 'country', 'city']