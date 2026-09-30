from rest_framework import viewsets, generics, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiParameter,
)
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Q, Prefetch, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ItineraryFilter

from .models import (
    Itinerary,
    ItineraryItem,
    ItineraryCollaboration,
)
from .serializers import (
    ItinerarySerializer,
    ItineraryItemSerializer,
    ItineraryListSerializer,
    ItineraryCreateSerializer,
    ItineraryUpdateSerializer,
    ItineraryCollaborationSerializer,
)
from .permissions import (
    IsItineraryItemOwnerOrAdmin,
    IsItineraryOwnerOrAdmin,
    IsOwnerOrCollaboratorOrAdmin,
)


def items_with_destinations():
    """
    ItineraryItem queryset that loads everything the nested destination
    serializer touches (creator, amenities and each amenity) up front, so
    rendering N items costs a fixed number of queries rather than 3N.
    """
    return ItineraryItem.objects.select_related(
        'destination__created_by'
    ).prefetch_related(
        'destination__destination_amenities__amenity'
    )


class ItineraryViewSet(viewsets.ModelViewSet):
    """
    CRUD for itineraries the user owns, collaborates on, or that are public.

    Filters: ?status=planned&is_public=true&start_date_after=2026-06-01
    Search:  ?search=lisbon

    Example request (POST /api/v1/itineraries/):
        {"title": "Lisbon long weekend", "start_date": "2026-11-05",
         "end_date": "2026-11-08", "status": "draft"}

    Example response (201): the created itinerary with its id and dates.
    An end_date earlier than start_date is rejected with a 400.
    """
    serializer_class = ItinerarySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrCollaboratorOrAdmin
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = ItineraryFilter
    search_fields = [
        'title',
        'description',
    ]

    def get_serializer_class(self):
        if self.action == 'list':
            return ItineraryListSerializer

        if self.action == 'create':
            return ItineraryCreateSerializer

        if self.action in ['update', 'partial_update']:
            return ItineraryUpdateSerializer

        return ItinerarySerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Itinerary.objects.none()
        user = self.request.user

        base = Itinerary.objects.select_related('owner')

        if self.action == 'list':
            # The list serializer shows a handful of columns and no items.
            base = base.only(
                'id', 'title', 'start_date', 'end_date', 'status',
                'is_public', 'created_at', 'owner__username'
            )
        else:
            # Detail views render the nested day-by-day items, so load them
            # (with their destinations) in one extra query.
            base = base.prefetch_related(
                Prefetch('items', queryset=items_with_destinations())
            )

        if user.is_site_admin:
            return base.all()

        # Include itineraries owned by the user, publicly shared itineraries,
        # and private itineraries where the user is an assigned collaborator.
        return base.filter(
            Q(owner=user)
            | Q(is_public=True)
            | Q(collaborations__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def public(self, request):
        public_itineraries = (
            Itinerary.objects
            .select_related('owner')
            .prefetch_related(
                Prefetch('items', queryset=items_with_destinations())
            )
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

    @action(detail=True, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request, pk=None):
        """
        GET /api/v1/itineraries/<id>/export-pdf/

        Generate a simple PDF summary of the itinerary (title, dates,
        status, day-by-day items). Returns application/pdf.
        """
        from io import BytesIO
        from django.http import HttpResponse

        itinerary = self.get_object()
        items = (
            itinerary.items
            .select_related('destination')
            .order_by('day_number', 'order')
        )

        lines = [
            f'Trip: {itinerary.title}',
            f'Owner: {itinerary.owner.username}',
            f'Status: {itinerary.status}',
            f'Dates: {itinerary.start_date} to {itinerary.end_date}',
            f'Duration: {itinerary.calculate_duration()} days',
            '',
            'Day-by-day plan:',
        ]
        for item in items:
            extra = f' — {item.notes}' if item.notes else ''
            lines.append(
                f'  Day {item.day_number}: {item.destination.name}{extra}'
            )
        if not items:
            lines.append('  (no items yet)')

        def _esc(text):
            return (
                str(text)
                .replace('\\', '\\\\')
                .replace('(', '\\(')
                .replace(')', '\\)')
            )

        content_lines = []
        y = 750
        for line in lines:
            content_lines.append(
                f'BT /F1 11 Tf 50 {y} Td ({_esc(line)[:90]}) Tj ET'
            )
            y -= 16
            if y < 50:
                break
        stream = '\n'.join(content_lines)
        stream_bytes = stream.encode('latin-1', errors='replace')

        objects = []
        objects.append(b'1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n')
        objects.append(
            b'2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n'
        )
        objects.append(
            b'3 0 obj<< /Type /Page /Parent 2 0 R '
            b'/MediaBox [0 0 612 792] '
            b'/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> '
            b'>>endobj\n'
        )
        objects.append(
            f'4 0 obj<< /Length {len(stream_bytes)} >>stream\n'.encode()
            + stream_bytes
            + b'\nendstream\nendobj\n'
        )
        objects.append(
            b'5 0 obj<< /Type /Font /Subtype /Type1 '
            b'/BaseFont /Helvetica >>endobj\n'
        )

        buffer = BytesIO()
        buffer.write(b'%PDF-1.4\n')
        offsets = [0]
        for obj in objects:
            offsets.append(buffer.tell())
            buffer.write(obj)
        xref_pos = buffer.tell()
        buffer.write(f'xref\n0 {len(offsets)}\n'.encode())
        buffer.write(b'0000000000 65535 f \n')
        for off in offsets[1:]:
            buffer.write(f'{off:010d} 00000 n \n'.encode())
        buffer.write(
            f'trailer<< /Size {len(offsets)} /Root 1 0 R >>\n'
            f'startxref\n{xref_pos}\n%%EOF\n'.encode()
        )

        pdf_bytes = buffer.getvalue()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f'itinerary-{itinerary.id}.pdf'
        response['Content-Disposition'] = (
            f'attachment; filename="{filename}"'
        )

        try:
            from bookings.views import log_activity
            from bookings.models import ActivityLog
            log_activity(
                request.user,
                ActivityLog.ActionChoices.EXPORT,
                'itinerary',
                itinerary.id,
                description=f'Exported PDF for {itinerary.title}',
                request=request,
            )
        except Exception:
            pass

        return response


class ItineraryItemListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/itineraries/<itinerary_id>/items/ - list the day-by-day items
    POST /api/v1/itineraries/<itinerary_id>/items/ - add a destination to a day

    Who may do what is decided by IsItineraryItemOwnerOrAdmin: the owner and
    'editor'/'admin' collaborators can add items, 'viewer' collaborators can
    only read.

    Example request (POST):
        {"destination": 4, "day_number": 2, "notes": "Sunset at the pier"}

    Example response (201):
        {"id": 12, "destination_detail": {"name": "Lisbon", ...},
         "day_number": 2, "notes": "Sunset at the pier", "order": 0}
    """
    serializer_class = ItineraryItemSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsItineraryItemOwnerOrAdmin
    ]

    def get_itinerary(self):
        # Cached on the view so the permission class, serializer and
        # queryset share one database lookup per request.
        if not hasattr(self, '_itinerary'):
            try:
                self._itinerary = Itinerary.objects.select_related(
                    'owner'
                ).get(pk=self.kwargs['itinerary_id'])
            except Itinerary.DoesNotExist:
                raise NotFound("Itinerary not found.")
        return self._itinerary

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ItineraryItem.objects.none()

        return items_with_destinations().filter(
            itinerary=self.get_itinerary()
        )

    def perform_create(self, serializer):
        serializer.save(itinerary=self.get_itinerary())


class ItineraryCollaborationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/itineraries/<itinerary_id>/collaborators/ - list collaborators
    POST /api/v1/itineraries/<itinerary_id>/collaborators/ - invite someone

    Owner only. Roles are 'viewer' (read), 'editor' (edit) or 'admin'.

    Example request (POST): {"user": 7, "role": "editor"}
    Example response (201): {"id": 3, "user": 7, "username": "sam",
                             "role": "editor", "itinerary": 12}
    """
    serializer_class = ItineraryCollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_itinerary(self):
        return get_object_or_404(
            Itinerary,
            pk=self.kwargs['itinerary_id']
        )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ItineraryCollaboration.objects.none()

        itinerary = self.get_itinerary()
        # Collaborators can only be managed by the owner of the itinerary.
        if itinerary.owner != self.request.user:
            raise PermissionDenied(
                "Only the itinerary owner can manage collaborators."
            )

        return ItineraryCollaboration.objects.select_related(
            'user',
            'itinerary'
        ).filter(
            itinerary=itinerary
        )

    def perform_create(self, serializer):
        itinerary = self.get_itinerary()
        if itinerary.owner != self.request.user:
            raise PermissionDenied(
                "Only the itinerary owner can add collaborators."
            )
        # Attach the collaboration to the itinerary from the URL.
        serializer.save(itinerary=itinerary)


class ItineraryCollaboratorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/itineraries/<itinerary_id>/collaborators/<user_id>/
    PATCH  ...  change the collaborator's role
    DELETE ...  remove the collaborator from the itinerary

    Owner (or site admin) only.

    Example request (PATCH): {"role": "viewer"}
    Example response (200): {"id": 3, "user": 7, "username": "sam",
                             "role": "viewer", "itinerary": 12}
    """
    serializer_class = ItineraryCollaborationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsItineraryOwnerOrAdmin
    ]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ItineraryCollaboration.objects.none()

        return ItineraryCollaboration.objects.select_related(
            'user',
            'itinerary__owner'
        ).filter(itinerary_id=self.kwargs['itinerary_id'])


@extend_schema(
    methods=['GET'],
    responses=inline_serializer(
        name='ItineraryStatusResponse',
        fields={
            'itinerary_id': serializers.IntegerField(),
            'title': serializers.CharField(),
            'status': serializers.CharField(),
        },
    ),
)
@extend_schema(
    methods=['PATCH'],
    request=inline_serializer(
        name='ItineraryStatusRequest',
        fields={
            'status': serializers.CharField(),
        },
    ),
    responses=inline_serializer(
        name='ItineraryStatusUpdateResponse',
        fields={
            'itinerary_id': serializers.IntegerField(),
            'title': serializers.CharField(),
            'status': serializers.CharField(),
        },
    ),
)
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
        or getattr(request.user, 'role', None) == 'admin'
    ):
        return Response(
            {
                "detail": (
                    "You do not have permission to manage "
                    "this itinerary."
                )
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
        # Only allow status values defined by the itinerary model choices.
        new_status = request.data.get('status')
        valid_statuses = dict(Itinerary.Status.choices)
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


@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(
            name='q', type=str, location=OpenApiParameter.QUERY,
            description='Free-text search on title/description',
            required=False,
        ),
        OpenApiParameter(
            name='status', type=str, location=OpenApiParameter.QUERY,
            description='Filter by itinerary status', required=False,
        ),
        OpenApiParameter(
            name='start_after', type=str, location=OpenApiParameter.QUERY,
            description='Start date on or after (YYYY-MM-DD)', required=False,
        ),
        OpenApiParameter(
            name='start_before', type=str, location=OpenApiParameter.QUERY,
            description='Start date on or before (YYYY-MM-DD)', required=False,
        ),
        OpenApiParameter(
            name='is_public', type=bool, location=OpenApiParameter.QUERY,
            description='Filter by public flag', required=False,
        ),
    ],
    responses={
        200: inline_serializer(
            name='TripSearchResponse',
            fields={
                'count': serializers.IntegerField(),
                'results': serializers.ListField(),
            },
        ),
    },
    description='Search itineraries with custom filters and ranking.',
)
@extend_schema(
    methods=['POST'],
    request=inline_serializer(
        name='TripSearchSaveRequest',
        fields={
            'q': serializers.CharField(required=False),
            'status': serializers.CharField(required=False),
            'start_after': serializers.CharField(required=False),
            'start_before': serializers.CharField(required=False),
            'is_public': serializers.BooleanField(required=False),
        },
    ),
    responses={
        200: inline_serializer(
            name='TripSearchSaveResponse',
            fields={
                'detail': serializers.CharField(),
                'saved': serializers.DictField(),
            },
        ),
    },
    description='Save search preferences onto the user profile.',
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def trip_search(request):
    """
    GET  /api/v1/itineraries/search/
         Search itineraries with custom filters and simple ranking.
    POST /api/v1/itineraries/search/
         Save search preferences onto the user profile
         (travel_preferences['last_trip_search']).

    Query params (GET):
        q          - free-text search on title/description
        status     - itinerary status
        start_after / start_before - date filters
        is_public  - true/false
    """
    if request.method == 'POST':
        prefs = dict(request.user.travel_preferences or {})
        prefs['last_trip_search'] = request.data
        request.user.travel_preferences = prefs
        request.user.save(update_fields=['travel_preferences', 'updated_at'])
        return Response(
            {
                'detail': 'Search preferences saved.',
                'saved': prefs['last_trip_search']
            },
            status=200,
        )

    # GET — custom search with ranking
    q = request.query_params.get('q', '').strip()
    status_filter = request.query_params.get('status')
    start_after = request.query_params.get('start_after')
    start_before = request.query_params.get('start_before')
    is_public = request.query_params.get('is_public')

    user = request.user
    qs = (
        Itinerary.objects
        .select_related('owner')
        .prefetch_related('items')
        .annotate(item_count=Count('items'))
        .filter(
            Q(owner=user)
            | Q(is_public=True)
            | Q(collaborations__user=user)
        )
        .distinct()
    )

    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )
    if status_filter:
        qs = qs.filter(status=status_filter)
    if start_after:
        qs = qs.filter(start_date__gte=start_after)
    if start_before:
        qs = qs.filter(start_date__lte=start_before)
    if is_public is not None:
        qs = qs.filter(is_public=is_public.lower() in ('1', 'true', 'yes'))

    # Simple ranking: public + more items + sooner start_date rank higher
    results = list(qs[:50])

    def rank(it):
        score = 0
        if it.is_public:
            score += 2
        score += min(getattr(it, 'item_count', 0), 10)
        if it.owner_id == user.id:
            score += 3
        return score

    results.sort(key=rank, reverse=True)
    serializer = ItineraryListSerializer(results, many=True)
    return Response({
        'count': len(results),
        'results': serializer.data,
    })
