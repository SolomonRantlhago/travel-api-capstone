from rest_framework import generics, permissions
from .models import Booking
from .serializers import BookingSerializer
from .permissions import IsBookingOwnerOrAdmin


class BookingListCreateView(generics.ListCreateAPIView):
    """
    GET /api/bookings/ - list the logged-in user's own bookings (all bookings if admin)
    POST /api/bookings/ - create a new booking (must own the itinerary being booked)
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(booked_by=user)

    def perform_create(self, serializer):
        serializer.save(booked_by=self.request.user)


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/bookings/<id>/ - manage a specific booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingOwnerOrAdmin]