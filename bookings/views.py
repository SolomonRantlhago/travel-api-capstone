from django.db import transaction
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework.response import Response

from .models import Booking, Accommodation, Activity, ActivityLog
from .serializers import (
    BookingSerializer,
    BookingListSerializer,
    AccommodationSerializer,
    ActivitySerializer,
    ActivityLogSerializer,
)
from .permissions import IsBookingOwnerOrAdmin
from .filters import BookingFilter


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_activity(user, action, entity_type, entity_id=None,
                 description='', metadata=None, request=None):
    """Write an audit log entry (best-effort; never raises)."""
    try:
        ActivityLog.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            metadata=metadata or {},
            ip_address=_client_ip(request) if request else None,
        )
    except Exception:
        pass


class AccommodationViewSet(viewsets.ModelViewSet):
    """
    Browse and manage accommodations (hotels, hostels, rentals, etc.).
    """
    queryset = Accommodation.objects.select_related('destination').all()
    serializer_class = AccommodationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['destination', 'accommodation_type', 'is_available']
    search_fields = ['name', 'description', 'address', 'destination__name']
    ordering_fields = ['price_per_night', 'name', 'created_at']


class ActivityViewSet(viewsets.ModelViewSet):
    """
    Browse and manage activities, tours and attractions.
    """
    queryset = Activity.objects.select_related('destination').all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['destination', 'category', 'is_available']
    search_fields = ['name', 'description', 'destination__name']
    ordering_fields = ['price', 'duration_hours', 'name', 'created_at']


class BookingViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for bookings. Users only see/manage their own bookings
    (admins see and manage all of them).

    Extra actions: POST /bookings/<id>/confirm/ and /bookings/<id>/cancel/
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        return BookingSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = BookingFilter
    search_fields = [
        'status',
        'itinerary__title',
        'reference_number',
    ]
    ordering_fields = [
        'created_at',
        'cost',
        'booking_date',
    ]

    def get_permissions(self):
        if self.action in [
            'update', 'partial_update', 'destroy', 'confirm', 'cancel'
        ]:
            return [permissions.IsAuthenticated(), IsBookingOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        base = Booking.objects.select_related(
            'booked_by',
            'itinerary',
            'accommodation',
            'activity',
        ).annotate(
            itinerary_item_count=Count('itinerary__items')
        ).order_by('-created_at')

        if user.is_site_admin:
            return base.all()
        return base.filter(booked_by=user)

    def perform_create(self, serializer):
        booking = serializer.save(booked_by=self.request.user)
        log_activity(
            self.request.user,
            ActivityLog.ActionChoices.BOOK,
            'booking',
            booking.id,
            description=f'Created booking {booking.reference_number}',
            request=self.request,
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        POST /api/v1/bookings/<id>/confirm/ - mark a pending booking as
        confirmed. Only the booking's owner or an admin can confirm it.

        Example response (200): the booking with "status": "confirmed".
        A booking that is not pending returns 400.
        """
        booking = self.get_object()

        if booking.status != 'pending':
            return Response(
                {
                    'detail': (
                        f"Booking is already '{booking.status}', "
                        'cannot confirm.'
                    )
                },
                status=400
            )

        booking.status = 'confirmed'
        booking.save(update_fields=['status', 'updated_at'])
        log_activity(
            request.user,
            ActivityLog.ActionChoices.CONFIRM,
            'booking',
            booking.id,
            description=f'Confirmed booking {booking.reference_number}',
            request=request,
        )
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        POST /api/v1/bookings/<id>/cancel/ - cancel a pending or confirmed
        booking. A booking that was already paid is marked 'refunded'.

        Example response (200): the booking with "status": "cancelled".
        Completed or already-cancelled bookings return 400.
        """
        booking = self.get_object()

        if not booking.is_active():
            return Response(
                {
                    'detail': (
                        f"Booking is already '{booking.status}', "
                        'cannot cancel.'
                    )
                },
                status=400
            )

        booking.status = 'cancelled'
        update_fields = ['status', 'updated_at']

        if booking.payment_status == 'paid':
            booking.payment_status = 'refunded'
            update_fields.append('payment_status')

        booking.save(update_fields=update_fields)
        log_activity(
            request.user,
            ActivityLog.ActionChoices.CANCEL,
            'booking',
            booking.id,
            description=f'Cancelled booking {booking.reference_number}',
            request=request,
        )
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only audit trail. Users see their own logs; admins see all.
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'entity_type']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ActivityLog.objects.none()
        qs = ActivityLog.objects.select_related('user')
        if self.request.user.is_site_admin:
            return qs
        return qs.filter(user=self.request.user)


@extend_schema(
    request=inline_serializer(
        name='BulkUpdateBookingsRequest',
        fields={
            'booking_ids': drf_serializers.ListField(
                child=drf_serializers.IntegerField(),
                help_text='IDs of bookings to update',
            ),
            'status': drf_serializers.ChoiceField(
                choices=Booking.StatusChoices.choices,
                required=False,
            ),
            'payment_status': drf_serializers.ChoiceField(
                choices=Booking.PaymentStatusChoices.choices,
                required=False,
            ),
        },
    ),
    responses={
        200: inline_serializer(
            name='BulkUpdateBookingsResponse',
            fields={
                'success_count': drf_serializers.IntegerField(),
                'failure_count': drf_serializers.IntegerField(),
                'results': drf_serializers.ListField(),
            },
        ),
        400: inline_serializer(
            name='BulkUpdateBookingsError',
            fields={'detail': drf_serializers.CharField()},
        ),
    },
    description=(
        'Update multiple bookings in a single atomic request. '
        'Only the owner (or admin) may update each booking.'
    ),
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_bookings(request):
    """
    POST /api/v1/bookings/bulk-update/

    Update multiple bookings in a single atomic request.

    Body example:
        {
            "booking_ids": [1, 2, 3],
            "status": "confirmed"
        }

    Returns success/failure counts and per-id results.
    Only the owner (or admin) may update each booking.
    """
    booking_ids = request.data.get('booking_ids') or []
    new_status = request.data.get('status')
    new_payment = request.data.get('payment_status')

    if not isinstance(booking_ids, list) or not booking_ids:
        return Response(
            {'detail': 'booking_ids must be a non-empty list.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    allowed_status = {c.value for c in Booking.StatusChoices}
    if new_status and new_status not in allowed_status:
        return Response(
            {'detail': f'status must be one of {sorted(allowed_status)}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    allowed_payment = {c.value for c in Booking.PaymentStatusChoices}
    if new_payment and new_payment not in allowed_payment:
        return Response(
            {
                'detail': (
                    f'payment_status must be one of '
                    f'{sorted(allowed_payment)}.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not new_status and not new_payment:
        return Response(
            {'detail': 'Provide status and/or payment_status to update.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    qs = Booking.objects.filter(id__in=booking_ids)
    if not user.is_site_admin:
        qs = qs.filter(booked_by=user)

    found = {b.id: b for b in qs}
    results = []
    success = 0
    failed = 0

    try:
        with transaction.atomic():
            for bid in booking_ids:
                booking = found.get(bid)
                if not booking:
                    results.append({
                        'id': bid,
                        'ok': False,
                        'error': 'Not found or not permitted.',
                    })
                    failed += 1
                    continue

                update_fields = ['updated_at']
                if new_status:
                    booking.status = new_status
                    update_fields.append('status')
                if new_payment:
                    booking.payment_status = new_payment
                    update_fields.append('payment_status')
                booking.save(update_fields=update_fields)
                results.append({'id': bid, 'ok': True})
                success += 1
                log_activity(
                    user,
                    ActivityLog.ActionChoices.UPDATE,
                    'booking',
                    bid,
                    description='Bulk update',
                    metadata={
                        'status': new_status,
                        'payment_status': new_payment,
                    },
                    request=request,
                )
    except Exception as exc:
        return Response(
            {'detail': f'Bulk update failed: {exc}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({
        'success_count': success,
        'failure_count': failed,
        'results': results,
    })
