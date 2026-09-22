from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, destination_reviews


app_name = 'reviews'


router = DefaultRouter()

router.register(
    r'',
    ReviewViewSet,
    basename='review'
)

urlpatterns = [
    path(
        'destination/<int:destination_id>/',
        destination_reviews,
        name='destination-reviews'
    ),
] + router.urls