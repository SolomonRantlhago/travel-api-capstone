from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Destination
from .serializers import DestinationSerializer
from .permissions import IsAdminOrReadOnly


class DestinationListCreateView(generics.ListCreateAPIView):
    """
    GET /api/destinations/ - list all destinations (anyone can view)
    POST /api/destinations/ - create a new destination (staff/admin only)
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price_range', 'country']
    search_fields = ['name', 'country', 'city', 'description']
    ordering_fields = ['created_at', 'name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DestinationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/destinations/<id>/ - view a single destination (anyone)
    PUT/PATCH/DELETE /api/destinations/<id>/ - staff/admin only
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]