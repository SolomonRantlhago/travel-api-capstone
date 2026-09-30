import django_filters
from .models import Itinerary


class ItineraryFilter(django_filters.FilterSet):

    # These filters allow clients to request itineraries within a date range.
    start_date_after = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte'
    )

    end_date_before = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte'
    )

    class Meta:
        model = Itinerary
        fields = [
            'status',
            'is_public',
        ]
