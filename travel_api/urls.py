"""
URL configuration for travel_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('blog/', views.home, name='home')
Class-based views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Including another URLconf
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'api/v1/accounts/',
        include(('accounts.urls', 'accounts'), namespace='accounts')
    ),

    path(
        'api/v1/destinations/',
        include(
            ('destinations.urls', 'destinations'),
            namespace='destinations'
        )
    ),

    path(
        'api/v1/itineraries/',
        include(
            ('itineraries.urls', 'itineraries'),
            namespace='itineraries'
        )
    ),

    path(
        'api/v1/bookings/',
        include(
            ('bookings.urls', 'bookings'),
            namespace='bookings'
        )
    ),

    path(
        'api/v1/reviews/',
        include(
            ('reviews.urls', 'reviews'),
            namespace='reviews'
        )
    ),

    path(
        'api/v1/budgets/',
        include(('budgets.urls', 'budgets'), namespace='budgets')
    ),
]