from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ItineraryViewSet,
    ItineraryItemListCreateView,
    itinerary_status,
)


app_name = 'itineraries'


router = DefaultRouter()

router.register(
    r'',
    ItineraryViewSet,
    basename='itinerary'
)

urlpatterns = [
    path(
        '<int:itinerary_id>/items/',
        ItineraryItemListCreateView.as_view(),
        name='itinerary-item-list-create'
    ),
    path(
        '<int:pk>/status/',
        itinerary_status,
        name='itinerary-status'
    ),
] + router.urls