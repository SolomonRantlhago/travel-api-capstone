from django.urls import path
from .views import (
    ItineraryListCreateView,
    ItineraryDetailView,
    ItineraryItemListCreateView,
)

urlpatterns = [
    path('', ItineraryListCreateView.as_view(), name='itinerary-list-create'),
    path('<int:pk>/', ItineraryDetailView.as_view(), name='itinerary-detail'),
    path('<int:itinerary_id>/items/', ItineraryItemListCreateView.as_view(), name='itinerary-item-list-create'),
]