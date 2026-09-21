from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework.exceptions import NotFound
from .models import Itinerary, ItineraryItem
from .serializers import ItinerarySerializer, ItineraryItemSerializer
from .permissions import IsOwnerOrAdminOrReadOnlyIfPublic


class ItineraryListCreateView(generics.ListCreateAPIView):
    """
    GET /api/itineraries/ - list the user's own itineraries + public ones from others
    POST /api/itineraries/ - create a new itinerary (must be logged in)
    """
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Itinerary.objects.all()
        return Itinerary.objects.filter(Q(owner=user) | Q(is_public=True))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ItineraryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/itineraries/<id>/ - view/edit/delete a specific itinerary
    """
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnlyIfPublic]


class ItineraryItemListCreateView(generics.ListCreateAPIView):
    """
    GET /api/itineraries/<itinerary_id>/items/ - list items for one itinerary
    POST /api/itineraries/<itinerary_id>/items/ - add a new item (owner or admin only)
    """
    serializer_class = ItineraryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_itinerary(self):
        try:
            return Itinerary.objects.get(pk=self.kwargs['itinerary_id'])
        except Itinerary.DoesNotExist:
            raise NotFound("Itinerary not found.")

    def get_queryset(self):
        return ItineraryItem.objects.filter(itinerary_id=self.kwargs['itinerary_id'])

    def perform_create(self, serializer):
        itinerary = self.get_itinerary()
        user = self.request.user
        if not (itinerary.owner == user or user.is_staff or user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this itinerary.")
        serializer.save(itinerary=itinerary)