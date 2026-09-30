import django_filters
from .models import Destination


class DestinationFilter(django_filters.FilterSet):
    # Use case-insensitive matching so users do not need exact capitalization.
    category = django_filters.CharFilter(
        field_name='category',
        lookup_expr='iexact'
    )

    country = django_filters.CharFilter(
        field_name='country',
        lookup_expr='iexact'
    )

    price_range = django_filters.CharFilter(
        field_name='price_range',
        lookup_expr='iexact'
    )

    class Meta:
        model = Destination
        fields = [
            'category',
            'country',
            'price_range',
        ]
