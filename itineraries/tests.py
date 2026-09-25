from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from destinations.models import Destination
from .models import Itinerary, ItineraryItem


User = get_user_model()


class ItineraryObjectPermissionTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='itineraryowner',
            email='itineraryowner@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='itineraryother',
            email='itineraryother@example.com',
            password='TestPassword123!'
        )

        self.admin = User.objects.create_user(
            username='itineraryadmin',
            email='itineraryadmin@example.com',
            password='TestPassword123!',
            is_staff=True
        )

        self.private_itinerary = Itinerary.objects.create(
            title='Private Cape Town Trip',
            description='Private trip.',
            owner=self.owner,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=False
        )

        self.public_itinerary = Itinerary.objects.create(
            title='Public Durban Trip',
            description='Public trip.',
            owner=self.owner,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            status='planned',
            is_public=True
        )

    def test_owner_can_view_private_itinerary(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(
            f'/api/v1/itineraries/{self.private_itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_owner_can_update_private_itinerary(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f'/api/v1/itineraries/{self.private_itinerary.id}/',
            {'title': 'Updated Private Trip'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_owner_can_delete_private_itinerary(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(
            f'/api/v1/itineraries/{self.private_itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_other_user_can_view_public_itinerary(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(
            f'/api/v1/itineraries/{self.public_itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_other_user_cannot_view_private_itinerary(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(
            f'/api/v1/itineraries/{self.private_itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_other_user_cannot_update_public_itinerary(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            f'/api/v1/itineraries/{self.public_itinerary.id}/',
            {'title': 'Trying to Change It'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_other_user_cannot_delete_public_itinerary(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(
            f'/api/v1/itineraries/{self.public_itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_view_private_itinerary(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'/api/v1/itineraries/{self.private_itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_can_update_private_itinerary(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f'/api/v1/itineraries/{self.private_itinerary.id}/',
            {'title': 'Admin Updated Trip'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_can_delete_private_itinerary(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f'/api/v1/itineraries/{self.private_itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )


class ItineraryItemObjectPermissionTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='itemowner',
            email='itemowner@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='itemother',
            email='itemother@example.com',
            password='TestPassword123!'
        )

        self.admin = User.objects.create_user(
            username='itemadmin',
            email='itemadmin@example.com',
            password='TestPassword123!',
            is_staff=True
        )

        self.destination = Destination.objects.create(
            name='Cape Town',
            country='South Africa',
            description='Beautiful coastal city.'
        )

        self.itinerary = Itinerary.objects.create(
            title='Cape Town Trip',
            description='Trip itinerary.',
            owner=self.owner,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=False
        )

        self.item = ItineraryItem.objects.create(
            itinerary=self.itinerary,
            destination=self.destination,
            day_number=1,
            notes='Visit Table Mountain.',
            order=1
        )

        self.url = (
            f'/api/v1/itineraries/'
            f'{self.itinerary.id}/items/'
        )

    def test_owner_can_view_itinerary_items(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_other_user_cannot_view_itinerary_items(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_view_itinerary_items(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_owner_can_create_itinerary_item(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.url,
            {
                'destination': self.destination.id,
                'day_number': 2,
                'notes': 'Visit the waterfront.',
                'order': 1
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_other_user_cannot_create_itinerary_item(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.url,
            {
                'destination': self.destination.id,
                'day_number': 2,
                'notes': 'Trying to add an item.',
                'order': 1
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_create_itinerary_item(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.url,
            {
                'destination': self.destination.id,
                'day_number': 2,
                'notes': 'Admin adding an item.',
                'order': 1
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_nonexistent_itinerary_returns_404(self):
        self.client.force_authenticate(user=self.owner)

        url = '/api/v1/itineraries/999999/items/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

class ItineraryFunctionalityTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='itineraryuser',
            email='itineraryuser@example.com',
            password='TestPassword123!'
        )

        self.url = '/api/v1/itineraries/'

    def test_user_can_create_itinerary(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'title': 'Johannesburg Trip',
                'description': 'A trip to Johannesburg.',
                'start_date': '2026-12-01',
                'end_date': '2026-12-07',
                'status': 'planned',
                'is_public': False
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        itinerary = Itinerary.objects.get(
            title='Johannesburg Trip'
        )

        self.assertEqual(
            itinerary.owner,
            self.user
        )

    def test_user_can_list_itineraries(self):
        Itinerary.objects.create(
            title='Cape Town Trip',
            description='A trip to Cape Town.',
            owner=self.user,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            1
        )

        self.assertEqual(
            response.data['results'][0]['title'],
            'Cape Town Trip'
        )

    def test_user_can_retrieve_itinerary(self):
        itinerary = Itinerary.objects.create(
            title='Durban Trip',
            description='A trip to Durban.',
            owner=self.user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/itineraries/{itinerary.id}/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['title'],
            'Durban Trip'
        )

        self.assertEqual(
            response.data['description'],
            'A trip to Durban.'
        )

        self.assertEqual(
            response.data['owner'],
            self.user.id
        )

    def test_user_can_get_itinerary_status(self):
        itinerary = Itinerary.objects.create(
            title='Status Test Trip',
            description='Testing itinerary status.',
            owner=self.user,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/itineraries/{itinerary.id}/status/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['itinerary_id'],
            itinerary.id
        )

        self.assertEqual(
            response.data['title'],
            'Status Test Trip'
        )

        self.assertEqual(
            response.data['status'],
            'planned'
        )

    def test_public_endpoint_returns_public_itineraries(self):
        Itinerary.objects.create(
            title='Public Cape Town Trip',
            description='A public trip to Cape Town.',
            owner=self.user,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=True
        )

        Itinerary.objects.create(
            title='Private Durban Trip',
            description='A private trip to Durban.',
            owner=self.user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/api/v1/itineraries/public/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            1
        )

        self.assertEqual(
            response.data['results'][0]['title'],
            'Public Cape Town Trip'
        )
    def test_public_endpoint_without_pagination(self):
        Itinerary.objects.create(
            title='Public Trip Without Pagination',
            description='Testing non-paginated response.',
            owner=self.user,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=True
        )

        self.client.force_authenticate(user=self.user)

        with patch(
            'itineraries.views.ItineraryViewSet.paginate_queryset',
            return_value=None
        ):
            response = self.client.get(
                '/api/v1/itineraries/public/'
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['title'],
            'Public Trip Without Pagination'
        )
    def test_user_can_update_itinerary(self):
        itinerary = Itinerary.objects.create(
            title='Original Trip',
            description='Original description.',
            owner=self.user,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/itineraries/{itinerary.id}/'

        response = self.client.patch(
            url,
            {'title': 'Updated Trip'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        itinerary.refresh_from_db()

        self.assertEqual(
            itinerary.title,
            'Updated Trip'
        )

    def test_user_can_delete_itinerary(self):
        itinerary = Itinerary.objects.create(
            title='Trip To Delete',
            description='This itinerary will be deleted.',
            owner=self.user,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/itineraries/{itinerary.id}/'

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Itinerary.objects.filter(
                id=itinerary.id
            ).exists()
        )

    def test_user_can_list_itinerary_items(self):
        itinerary = Itinerary.objects.create(
            title='Cape Town Trip',
            description='A trip to Cape Town.',
            owner=self.user,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=False
        )

        destination = Destination.objects.create(
            name='Table Mountain',
            country='South Africa',
            description='A famous mountain in Cape Town.'
        )

        ItineraryItem.objects.create(
            itinerary=itinerary,
            destination=destination,
            day_number=1,
            notes='Visit Table Mountain.',
            order=1
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/itineraries/{itinerary.id}/items/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            1
        )

        self.assertEqual(
            response.data['results'][0]['notes'],
            'Visit Table Mountain.'
        )

    def test_user_can_create_itinerary_item(self):
        itinerary = Itinerary.objects.create(
            title='Durban Trip',
            description='Trip to Durban.',
            owner=self.user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            status='planned',
            is_public=False
        )

        destination = Destination.objects.create(
            name='uShaka Marine World',
            country='South Africa',
            description='A popular attraction in Durban.'
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/itineraries/{itinerary.id}/items/'

        response = self.client.post(
            url,
            {
                'destination': destination.id,
                'day_number': 2,
                'notes': 'Visit uShaka Marine World.',
                'order': 1
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        item = ItineraryItem.objects.get(
            itinerary=itinerary
        )

        self.assertEqual(
            item.destination,
            destination
        )

        self.assertEqual(
            item.day_number,
            2
        )

        self.assertEqual(
            item.notes,
            'Visit uShaka Marine World.'
        )

    def test_unauthenticated_user_cannot_list_public_itineraries(self):
        response = self.client.get(
            '/api/v1/itineraries/public/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
    def test_other_user_cannot_get_itinerary_status(self):
        other_user = User.objects.create_user(
            username='other_status_user',
            password='testpass123'
        )

        itinerary = Itinerary.objects.create(
            title='Private Status Trip',
            description='Testing status permissions.',
            owner=self.user,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=other_user)

        url = f'/api/v1/itineraries/{itinerary.id}/status/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.data['detail'],
            'You do not have permission to manage this itinerary.'
        )
    def test_user_can_update_itinerary_status(self):
        itinerary = Itinerary.objects.create(
            title='Status Update Trip',
            description='Testing status update.',
            owner=self.user,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 7),
            status='planned',
            is_public=False
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/itineraries/{itinerary.id}/status/'

        response = self.client.patch(
            url,
            {'status': 'completed'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['status'],
            'completed'
        )

        itinerary.refresh_from_db()

        self.assertEqual(
            itinerary.status,
            'completed'
        )
    def test_invalid_itinerary_status_returns_400(self):
        itinerary = Itinerary.objects.create(
            title='Invalid Status Trip',
            description='Testing invalid status.',
            owner=self.user,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 7),
            status='planned',
            is_public=False
        )
    
        self.client.force_authenticate(user=self.user)
    
        url = f'/api/v1/itineraries/{itinerary.id}/status/'
    
        response = self.client.patch(
            url,
            {'status': 'invalid_status'},
            format='json'
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
    
        self.assertIn(
            'status',
            response.data
        )