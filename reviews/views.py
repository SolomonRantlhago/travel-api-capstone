from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewOwnerOrAdminOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for reviews. Anyone can read; only the author or an
    admin can update/delete a given review.
    """
    queryset = Review.objects.select_related('reviewer', 'destination').all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['destination', 'rating']
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsReviewOwnerOrAdminOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_reviews(self, request):
        """
        GET /api/reviews/my_reviews/ - list only the logged-in user's own reviews.
        """
        reviews = Review.objects.select_related('reviewer', 'destination').filter(reviewer=request.user)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)