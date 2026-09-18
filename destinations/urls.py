from django.urls import path
from .views import DestinationListCreateView, DestinationDetailView

urlpatterns = [
    path('', DestinationListCreateView.as_view(), name='destination-list-create'),
    path('<int:pk>/', DestinationDetailView.as_view(), name='destination-detail'),
]