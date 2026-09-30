import django_filters
from .models import Booking


class BookingFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact'
    )

    # The date filters let clients restrict bookings to a specific
    # creation period.
    booked_from = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )

    booked_until = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = Booking
        fields = [
            'status',
        ]
