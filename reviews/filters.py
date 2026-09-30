import django_filters
from .models import Review


class ReviewFilter(django_filters.FilterSet):

    # These filters allow clients to search for reviews within a rating range.
    min_rating = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte'
    )

    max_rating = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte'
    )

    class Meta:
        model = Review
        fields = [
            'destination',
            'rating',
        ]
