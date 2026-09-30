from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .filters import DestinationFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Prefetch, Q
from .models import Destination, DestinationAmenity
from .serializers import (
    DestinationSerializer,
    DestinationListSerializer,
    DestinationCreateSerializer,
    DestinationUpdateSerializer
)
from .permissions import IsAdminOrReadOnly
from .pagination import DestinationPagination


class DestinationViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for destinations. Anyone can browse/search; only
    staff/admin can create, update, or delete entries.

    Example: GET /api/v1/destinations/?category=beach&search=bali&ordering=name

    Example response (200):
        {"count": 1, "next": null, "previous": null,
         "results": [{"id": 3, "name": "Bali", "country": "Indonesia",
                      "category": "beach", "price_range": "moderate"}]}
    """
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DestinationPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DestinationFilter
    search_fields = ['name', 'country', 'city', 'description']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        """
        Pick the cheapest queryset for the action:
        * list      - only the columns the list serializer shows
        * otherwise - full rows plus the creator and amenities loaded
                      up front, so the detail view avoids N+1 queries
        """
        if self.action == 'list':
            return Destination.objects.only(
                'id', 'name', 'country', 'city',
                'category', 'price_range', 'image', 'created_at'
            )

        return Destination.objects.select_related(
            'created_by'
        ).prefetch_related(
            Prefetch(
                'destination_amenities',
                queryset=DestinationAmenity.objects.select_related('amenity')
            )
        )

    def get_serializer_class(self):
        if self.action in ('list', 'top_rated'):
            return DestinationListSerializer

        if self.action == 'create':
            return DestinationCreateSerializer

        if self.action in ['update', 'partial_update']:
            return DestinationUpdateSerializer

        return DestinationSerializer

    def perform_create(self, serializer):
        # Record the authenticated user as the creator of the destination.
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """
        GET /api/v1/destinations/top_rated/ - the 5 highest-rated destinations,
        based on average review rating. Destinations with no reviews are
        excluded.
        """
        top = (
            Destination.objects
            .defer('description')
            # Calculate average ratings and review counts for each destination.
            .annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            )
            # Exclude destinations that have no reviews so they cannot
            # appear as top-rated.
            .filter(
                Q(review_count__gt=0)
            )
            .order_by('-avg_rating')[:5]
        )
        serializer = self.get_serializer(top, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='recommendations')
    def recommendations(self, request):
        """
        GET /api/v1/destinations/recommendations/

        Personalized destination suggestions based on the user's
        travel_preferences, favorite destinations, and categories
        they have reviewed or booked via itineraries.

        Ranking factors (higher = better):
        - Matching preferred categories / price ranges
        - Already favorited destinations (boost)
        - Average review rating
        - Number of reviews (popularity)
        """
        user = request.user
        prefs = getattr(user, 'travel_preferences', None) or {}
        preferred_categories = set(prefs.get('categories', []) or [])
        preferred_price = prefs.get('price_range')
        preferred_countries = set(prefs.get('countries', []) or [])

        favorite_ids = set(
            user.favorite_destinations.values_list('id', flat=True)
        )

        # Categories the user has engaged with via reviews
        reviewed_categories = set(
            Destination.objects.filter(
                reviews__reviewer=user
            ).values_list('category', flat=True)
        )
        preferred_categories |= reviewed_categories

        qs = (
            Destination.objects
            .annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews'),
            )
            .select_related('created_by')
        )

        scored = []
        for dest in qs:
            score = 0.0
            if dest.category in preferred_categories:
                score += 3.0
            if preferred_price and dest.price_range == preferred_price:
                score += 2.0
            if dest.country in preferred_countries:
                score += 1.5
            if dest.id in favorite_ids:
                score += 4.0
            if dest.avg_rating:
                score += float(dest.avg_rating)
            if dest.review_count:
                score += min(dest.review_count, 10) * 0.1
            scored.append((score, dest))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        top = [d for _, d in scored[:10]]
        serializer = DestinationListSerializer(top, many=True)
        return Response({
            'count': len(top),
            'preferences_used': {
                'categories': list(preferred_categories),
                'price_range': preferred_price,
                'countries': list(preferred_countries),
                'favorite_count': len(favorite_ids),
            },
            'results': serializer.data,
        })
