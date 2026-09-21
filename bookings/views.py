from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Booking
from .serializers import BookingSerializer
from .permissions import IsBookingOwnerOrAdmin


class BookingViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for bookings. Users only see/manage their own bookings
    (admins see and manage all of them).
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        base = Booking.objects.select_related('booked_by', 'itinerary')
        if user.is_staff or user.is_superuser:
            return base.all()
        return base.filter(booked_by=user)

    def perform_create(self, serializer):
        serializer.save(booked_by=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        POST /api/bookings/<id>/confirm/ - mark a pending booking as confirmed.
        Only the booking's owner or an admin can confirm it.
        """
        booking = self.get_object()
        if not (booking.booked_by == request.user or request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied("You do not own this booking.")

        if booking.status != 'pending':
            return Response(
                {"detail": f"Booking is already '{booking.status}', cannot confirm."},
                status=400
            )

        booking.status = 'confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)