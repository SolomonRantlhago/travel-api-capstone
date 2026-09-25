from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewOwnerOrAdminOrReadOnly
from destinations.models import Destination


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for reviews. Anyone can read; only the author or an
    admin can update/delete a given review.
    """
    queryset = Review.objects.select_related(
        'reviewer',
        'destination'
    ).all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['destination', 'rating']
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        if self.action in ['create', 'my_reviews']:
            return [permissions.IsAuthenticated()]

        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsReviewOwnerOrAdminOrReadOnly()]

        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def my_reviews(self, request):
        """
        GET /api/reviews/my_reviews/ - list only the logged-in user's own reviews.
        """
        reviews = Review.objects.select_related(
            'reviewer',
            'destination'
        ).filter(
            reviewer=request.user
        )

        page = self.paginate_queryset(reviews)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def destination_reviews(request, destination_id):
    """
    GET  /api/v1/reviews/destination/<destination_id>/
    POST /api/v1/reviews/destination/<destination_id>/

    GET: List reviews for a destination.
    POST: Create a review for a destination.
    """
    destination = get_object_or_404(
        Destination,
        pk=destination_id
    )

    if request.method == 'GET':
        reviews = Review.objects.select_related(
            'reviewer',
            'destination'
        ).filter(
            destination=destination
        )

        serializer = ReviewSerializer(
            reviews,
            many=True
        )

        return Response(
            serializer.data,
            status=200
        )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                {
                    "detail": "Authentication credentials were not provided."
                },
                status=401
            )

        serializer = ReviewSerializer(
            data={
                **request.data,
                'destination': destination.id
            },
            context={'request': request}
        )

        if serializer.is_valid():
            review = serializer.save(
                destination=destination,
                reviewer=request.user
            )

            return Response(
                ReviewSerializer(review).data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )