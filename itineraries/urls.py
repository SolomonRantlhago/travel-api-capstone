from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ItineraryViewSet, ItineraryItemListCreateView

router = DefaultRouter()
router.register(r'', ItineraryViewSet, basename='itinerary')

urlpatterns = [
    path('<int:itinerary_id>/items/', ItineraryItemListCreateView.as_view(), name='itinerary-item-list-create'),
] + router.urls