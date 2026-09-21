from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from .models import Destination
from .serializers import DestinationSerializer
from .permissions import IsAdminOrReadOnly


class DestinationViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for destinations. Anyone can browse/search; only
    staff/admin can create, update, or delete entries.
    """
    queryset = Destination.objects.select_related('created_by').all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price_range', 'country']
    search_fields = ['name', 'country', 'city', 'description']
    ordering_fields = ['created_at', 'name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """
        GET /api/destinations/top_rated/ - the 5 highest-rated destinations,
        based on average review rating (destinations with no reviews are excluded).
        """
        top = (
            Destination.objects
            .annotate(avg_rating=Avg('reviews__rating'), review_count=Count('reviews'))
            .filter(review_count__gt=0)
            .order_by('-avg_rating')[:5]
        )
        serializer = self.get_serializer(top, many=True)
        return Response(serializer.data)