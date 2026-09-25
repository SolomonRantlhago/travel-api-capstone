from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Itinerary, ItineraryItem
from .serializers import ItinerarySerializer, ItineraryItemSerializer
from .permissions import (
    IsOwnerOrAdminOrReadOnlyIfPublic,
    IsItineraryItemOwnerOrAdmin,
)


class ItineraryViewSet(viewsets.ModelViewSet):
    serializer_class = ItinerarySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrAdminOrReadOnlyIfPublic
    ]

    def get_queryset(self):
        user = self.request.user

        base = Itinerary.objects.select_related(
            'owner'
        ).prefetch_related(
            'items__destination'
        )

        if user.is_staff or user.is_superuser:
            return base.all()

        return base.filter(
            Q(owner=user) | Q(is_public=True)
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def public(self, request):
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

        serializer = self.get_serializer(
            public_itineraries,
            many=True
        )

        return Response(serializer.data)


class ItineraryItemListCreateView(generics.ListCreateAPIView):
    serializer_class = ItineraryItemSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsItineraryItemOwnerOrAdmin
    ]

    def get_itinerary(self):
        try:
            return Itinerary.objects.get(
                pk=self.kwargs['itinerary_id']
            )
        except Itinerary.DoesNotExist:
            raise NotFound("Itinerary not found.")
    def get_queryset(self):
        itinerary = self.get_itinerary()
        user = self.request.user
    
        if user.is_staff or user.is_superuser:
            return ItineraryItem.objects.select_related(
                'destination'
            ).filter(
                itinerary=itinerary
            )
    
        if itinerary.owner != user:
            raise PermissionDenied(
                "You do not own this itinerary."
            )
    
        return ItineraryItem.objects.select_related(
            'destination'
        ).filter(
            itinerary=itinerary
        )

    def perform_create(self, serializer):
        itinerary = self.get_itinerary()
        user = self.request.user

        if not (
            itinerary.owner == user
            or user.is_staff
            or user.is_superuser
        ):
            raise PermissionDenied(
                "You do not own this itinerary."
            )

        serializer.save(itinerary=itinerary)


@api_view(['GET', 'PATCH'])
def itinerary_status(request, pk):
    """
    GET   /api/v1/itineraries/<id>/status/
    PATCH /api/v1/itineraries/<id>/status/

    GET: Return the current status of an itinerary.
    PATCH: Update the status of an itinerary.
    """
    itinerary = get_object_or_404(
        Itinerary,
        pk=pk
    )

    if not (
        itinerary.owner == request.user
        or request.user.is_staff
        or request.user.is_superuser
    ):
        return Response(
            {
                "detail": "You do not have permission to manage this itinerary."
            },
            status=403
        )

    if request.method == 'GET':
        return Response(
            {
                "itinerary_id": itinerary.id,
                "title": itinerary.title,
                "status": itinerary.status,
            },
            status=200
        )

    if request.method == 'PATCH':
        new_status = request.data.get('status')

        valid_statuses = dict(Itinerary.STATUS_CHOICES)

        if new_status not in valid_statuses:
            return Response(
                {
                    "status": (
                        f"Invalid status. Choose from: "
                        f"{', '.join(valid_statuses.keys())}."
                    )
                },
                status=400
            )

        itinerary.status = new_status
        itinerary.save(update_fields=['status', 'updated_at'])

        return Response(
            {
                "itinerary_id": itinerary.id,
                "title": itinerary.title,
                "status": itinerary.status,
            },
            status=200
        )