from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import Itinerary, ItineraryItem
from .serializers import ItinerarySerializer, ItineraryItemSerializer
from .permissions import IsOwnerOrAdminOrReadOnlyIfPublic


class ItineraryViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for itineraries. Users see their own itineraries plus
    anyone's public ones (admins see everything).
    """
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnlyIfPublic]

    def get_queryset(self):
        user = self.request.user
        base = Itinerary.objects.select_related('owner').prefetch_related('items__destination')

        if user.is_staff or user.is_superuser:
            return base.all()

        return base.filter(Q(owner=user) | Q(is_public=True))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def public(self, request):
        """
        GET /api/v1/itineraries/public/ - browse itineraries other users have made public.
        """
        public_itineraries = (
            Itinerary.objects
            .select_related('owner')
            .prefetch_related('items__destination')
            .filter(is_public=True)
        )

        page = self.paginate_queryset(public_itineraries)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(public_itineraries, many=True)
        return Response(serializer.data)


class ItineraryItemListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/itineraries/<itinerary_id>/items/ - list items for one itinerary
    POST /api/v1/itineraries/<itinerary_id>/items/ - add a new item (owner or admin only)
    """
    serializer_class = ItineraryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_itinerary(self):
        try:
            return Itinerary.objects.get(pk=self.kwargs['itinerary_id'])
        except Itinerary.DoesNotExist:
            raise NotFound("Itinerary not found.")

    def get_queryset(self):
        return ItineraryItem.objects.select_related(
            'destination'
        ).filter(
            itinerary_id=self.kwargs['itinerary_id']
        )

    def perform_create(self, serializer):
        itinerary = self.get_itinerary()
        user = self.request.user

        if not (itinerary.owner == user or user.is_staff or user.is_superuser):
            raise PermissionDenied("You do not own this itinerary.")

        serializer.save(itinerary=itinerary)
