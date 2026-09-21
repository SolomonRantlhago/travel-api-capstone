from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewOwnerOrAdminOrReadOnly


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET /api/reviews/ - list all reviews, filterable by destination or rating
    POST /api/reviews/ - create a new review (must be logged in)
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['destination', 'rating']
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/reviews/<id>/ - view a specific review (anyone)
    PUT/PATCH/DELETE /api/reviews/<id>/ - author or admin only
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrAdminOrReadOnly]