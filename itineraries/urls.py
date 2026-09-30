from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ItineraryViewSet,
    ItineraryItemListCreateView,
    ItineraryCollaborationListCreateView,
    ItineraryCollaboratorDetailView,
    itinerary_status,
    trip_search,
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
        '<int:itinerary_id>/collaborators/',
        ItineraryCollaborationListCreateView.as_view(),
        name='itinerary-collaborators'
    ),
    path(
        '<int:itinerary_id>/collaborators/<int:user_id>/',
        ItineraryCollaboratorDetailView.as_view(),
        name='itinerary-collaborator-detail'
    ),
    path(
        '<int:pk>/status/',
        itinerary_status,
        name='itinerary-status'
    ),
    path(
        'search/',
        trip_search,
        name='trip-search'
    ),
] + router.urls
