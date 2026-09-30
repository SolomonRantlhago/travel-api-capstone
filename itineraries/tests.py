from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from destinations.models import Destination
from .models import (
    Itinerary,
    ItineraryItem,
    ItineraryCollaboration,
)

from django.urls import reverse

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

    def test_role_admin_can_view_itinerary_items(self):
        role_admin = User.objects.create_user(
            username='roleadmin',
            email='roleadmin@example.com',
            password='TestPassword123!',
            role='admin'
        )

        self.client.force_authenticate(user=role_admin)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
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

    def test_user_can_upload_pdf_to_itinerary(self):
        self.client.force_authenticate(user=self.user)

        pdf_file = SimpleUploadedFile(
            'travel-plan.pdf',
            b'%PDF-1.4 fake pdf content',
            content_type='application/pdf'
        )

        response = self.client.post(
            self.url,
            {
                'title': 'PDF Trip',
                'description': 'Trip with a PDF.',
                'start_date': '2026-12-01',
                'end_date': '2026-12-07',
                'status': 'planned',
                'is_public': False,
                'pdf_file': pdf_file,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        itinerary = Itinerary.objects.get(
            title='PDF Trip'
        )

        self.assertTrue(
            itinerary.pdf_file.name
        )

    def test_non_pdf_file_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        invalid_file = SimpleUploadedFile(
            'travel-plan.txt',
            b'This is not a PDF file.',
            content_type='text/plain'
        )

        response = self.client.post(
            self.url,
            {
                'title': 'Invalid PDF Trip',
                'description': 'Trip with an invalid file.',
                'start_date': '2026-12-01',
                'end_date': '2026-12-07',
                'status': 'planned',
                'is_public': False,
                'pdf_file': invalid_file,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'pdf_file',
            response.data
        )

    def test_pdf_file_over_10mb_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        large_pdf = SimpleUploadedFile(
            'large-travel-plan.pdf',
            b'a' * (10 * 1024 * 1024 + 1),
            content_type='application/pdf'
        )

        response = self.client.post(
            self.url,
            {
                'title': 'Large PDF Trip',
                'description': 'Trip with a large PDF.',
                'start_date': '2026-12-01',
                'end_date': '2026-12-07',
                'status': 'planned',
                'is_public': False,
                'pdf_file': large_pdf,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'pdf_file',
            response.data
        )

    def test_role_admin_can_manage_itinerary_status(self):
        role_admin = User.objects.create_user(
            username='statusroleadmin',
            email='statusroleadmin@example.com',
            password='TestPassword123!',
            role='admin'
        )

        itinerary = Itinerary.objects.create(
            owner=self.user,
            title='Test Itinerary',
            description='Test description',
            start_date='2026-10-01',
            end_date='2026-10-05',
            is_public=False
        )

        self.client.force_authenticate(user=role_admin)

        response = self.client.get(
            reverse(
                'itineraries:itinerary-status',
                kwargs={'pk': itinerary.id}
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


class ItineraryCollaborationTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='collabowner',
            email='collabowner@example.com',
            password='TestPassword123!'
        )

        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collaborator@example.com',
            password='TestPassword123!'
        )

        self.itinerary = Itinerary.objects.create(
            title='Collaboration Trip',
            description='Trip for collaboration testing.',
            owner=self.owner,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=False
        )

        self.url = (
            f'/api/v1/itineraries/'
            f'{self.itinerary.id}/collaborators/'
        )

    def test_owner_can_add_collaborator(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.url,
            {
                'user': self.collaborator.id,
                'role': 'editor',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        collaboration = ItineraryCollaboration.objects.get(
            itinerary=self.itinerary,
            user=self.collaborator
        )

        self.assertEqual(
            collaboration.role,
            'editor'
        )

    def test_viewer_can_view_itinerary(self):
        ItineraryCollaboration.objects.create(
            itinerary=self.itinerary,
            user=self.collaborator,
            role='viewer'
        )

        self.client.force_authenticate(user=self.collaborator)

        response = self.client.get(
            f'/api/v1/itineraries/{self.itinerary.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_viewer_cannot_update_itinerary(self):
        ItineraryCollaboration.objects.create(
            itinerary=self.itinerary,
            user=self.collaborator,
            role='viewer'
        )

        self.client.force_authenticate(user=self.collaborator)

        response = self.client.patch(
            f'/api/v1/itineraries/{self.itinerary.id}/',
            {'title': 'Viewer Trying To Edit'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_editor_can_update_itinerary(self):
        ItineraryCollaboration.objects.create(
            itinerary=self.itinerary,
            user=self.collaborator,
            role='editor'
        )

        self.client.force_authenticate(user=self.collaborator)

        response = self.client.patch(
            f'/api/v1/itineraries/{self.itinerary.id}/',
            {'title': 'Editor Updated Trip'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.itinerary.refresh_from_db()

        self.assertEqual(
            self.itinerary.title,
            'Editor Updated Trip'
        )

    def test_admin_collaborator_can_update_itinerary(self):
        ItineraryCollaboration.objects.create(
            itinerary=self.itinerary,
            user=self.collaborator,
            role='admin'
        )

        self.client.force_authenticate(user=self.collaborator)

        response = self.client.patch(
            f'/api/v1/itineraries/{self.itinerary.id}/',
            {'title': 'Admin Collaborator Updated Trip'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.itinerary.refresh_from_db()

        self.assertEqual(
            self.itinerary.title,
            'Admin Collaborator Updated Trip'
        )


class ItineraryWriteValidationTests(APITestCase):
    """Date and PDF rules must hold on create AND update."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='validator', email='validator@test.com',
            password='TestPassword123!'
        )
        self.itinerary = Itinerary.objects.create(
            title='Existing', owner=self.user,
            start_date=date(2026, 10, 10), end_date=date(2026, 10, 20)
        )
        self.list_url = '/api/v1/itineraries/'
        self.detail_url = f'/api/v1/itineraries/{self.itinerary.id}/'
        self.client.force_authenticate(user=self.user)

    def test_create_rejects_end_date_before_start_date(self):
        response = self.client.post(
            self.list_url,
            {'title': 'Backwards', 'start_date': '2026-11-10',
             'end_date': '2026-11-01'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_date', response.data)
        self.assertFalse(Itinerary.objects.filter(title='Backwards').exists())

    def test_update_rejects_end_date_before_start_date(self):
        response = self.client.put(
            self.detail_url,
            {'title': 'Existing', 'start_date': '2026-11-10',
             'end_date': '2026-11-01'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_checks_against_stored_start_date(self):
        # Only end_date is sent; it precedes the STORED start_date (Oct 10)
        response = self.client.patch(
            self.detail_url, {'end_date': '2026-10-01'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.itinerary.refresh_from_db()
        self.assertEqual(self.itinerary.end_date, date(2026, 10, 20))

    def test_partial_update_with_valid_date_succeeds(self):
        response = self.client.patch(
            self.detail_url, {'end_date': '2026-10-25'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_rejects_non_pdf_upload(self):
        bad_file = SimpleUploadedFile(
            'malware.exe', b'MZ-not-a-pdf',
            content_type='application/x-msdownload'
        )

        response = self.client.patch(
            self.detail_url, {'pdf_file': bad_file}, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pdf_file', response.data)

    def test_pdf_with_wrong_extension_is_rejected(self):
        disguised = SimpleUploadedFile(
            'notes.txt', b'%PDF-1.4 content', content_type='application/pdf'
        )

        response = self.client.patch(
            self.detail_url, {'pdf_file': disguised}, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_accepts_valid_pdf(self):
        good = SimpleUploadedFile(
            'plan.pdf', b'%PDF-1.4 ok', content_type='application/pdf'
        )

        response = self.client.patch(
            self.detail_url, {'pdf_file': good}, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ItineraryItemRoleTests(APITestCase):
    """Owner / editor / viewer / stranger access to itinerary items."""

    def setUp(self):
        make = User.objects.create_user
        self.owner = make('iowner', 'io@test.com', 'TestPassword123!')
        self.editor = make('ieditor', 'ie@test.com', 'TestPassword123!')
        self.viewer = make('iviewer', 'iv@test.com', 'TestPassword123!')
        self.stranger = make('istranger', 'is@test.com', 'TestPassword123!')
        self.site_admin = make(
            'isiteadmin', 'isa@test.com', 'TestPassword123!', role='admin'
        )

        self.itinerary = Itinerary.objects.create(
            title='Role Trip', owner=self.owner,
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 7)
        )
        ItineraryCollaboration.objects.create(
            itinerary=self.itinerary, user=self.editor, role='editor'
        )
        ItineraryCollaboration.objects.create(
            itinerary=self.itinerary, user=self.viewer, role='viewer'
        )
        self.destination = Destination.objects.create(
            name='Porto', country='Portugal', description='Nice.',
            category='city', price_range='moderate'
        )
        self.url = f'/api/v1/itineraries/{self.itinerary.id}/items/'

    def _add(self, day=1):
        return self.client.post(
            self.url,
            {'destination': self.destination.id, 'day_number': day},
            format='json'
        )

    def test_owner_can_add_item(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self._add().status_code, status.HTTP_201_CREATED)

    def test_editor_collaborator_can_add_item(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self._add().status_code, status.HTTP_201_CREATED)

    def test_viewer_collaborator_cannot_add_item(self):
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(self._add().status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_collaborator_can_list_items(self):
        self.client.force_authenticate(user=self.viewer)
        self.assertEqual(
            self.client.get(self.url).status_code, status.HTTP_200_OK
        )

    def test_stranger_cannot_list_or_add_on_private_itinerary(self):
        self.client.force_authenticate(user=self.stranger)

        self.assertEqual(
            self.client.get(self.url).status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(self._add().status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_can_read_but_not_write_public_itinerary(self):
        self.itinerary.is_public = True
        self.itinerary.save()
        self.client.force_authenticate(user=self.stranger)

        self.assertEqual(
            self.client.get(self.url).status_code, status.HTTP_200_OK
        )
        self.assertEqual(self._add().status_code, status.HTTP_403_FORBIDDEN)

    def test_site_admin_can_add_item(self):
        self.client.force_authenticate(user=self.site_admin)
        self.assertEqual(self._add().status_code, status.HTTP_201_CREATED)

    def test_anonymous_gets_401(self):
        self.assertEqual(
            self.client.get(self.url).status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unknown_itinerary_returns_404(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/v1/itineraries/99999/items/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_duplicate_item_returns_400_not_500(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self._add(day=1).status_code, 201)

        response = self._add(day=1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            ItineraryItem.objects.filter(itinerary=self.itinerary).count(), 1
        )

    def test_same_destination_on_a_different_day_is_allowed(self):
        self.client.force_authenticate(user=self.owner)
        self._add(day=1)
        self.assertEqual(self._add(day=2).status_code, 201)

    def test_list_only_returns_items_of_this_itinerary(self):
        other = Itinerary.objects.create(
            title='Other', owner=self.owner,
            start_date=date(2026, 12, 1), end_date=date(2026, 12, 2)
        )
        ItineraryItem.objects.create(
            itinerary=other, destination=self.destination, day_number=1
        )
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(len(response.data['results']), 0)


class ItineraryCollaboratorManagementTests(APITestCase):
    """Update role / remove collaborator (owner only)."""

    def setUp(self):
        make = User.objects.create_user
        self.owner = make('cowner', 'co@test.com', 'TestPassword123!')
        self.member = make('cmember', 'cm@test.com', 'TestPassword123!')
        self.other = make('cother', 'cot@test.com', 'TestPassword123!')

        self.itinerary = Itinerary.objects.create(
            title='Team Trip', owner=self.owner,
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 7)
        )
        self.collab = ItineraryCollaboration.objects.create(
            itinerary=self.itinerary, user=self.member, role='viewer'
        )
        self.list_url = (
            f'/api/v1/itineraries/{self.itinerary.id}/collaborators/'
        )
        self.detail_url = f'{self.list_url}{self.member.id}/'

    def test_owner_can_change_role(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url, {'role': 'editor'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.collab.refresh_from_db()
        self.assertEqual(self.collab.role, 'editor')

    def test_patch_cannot_swap_the_collaborator_user(self):
        self.client.force_authenticate(user=self.owner)

        self.client.patch(
            self.detail_url,
            {'role': 'editor', 'user': self.other.id},
            format='json'
        )

        self.collab.refresh_from_db()
        self.assertEqual(self.collab.user, self.member)

    def test_owner_can_remove_collaborator(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ItineraryCollaboration.objects.filter(pk=self.collab.pk).exists()
        )

    def test_collaborator_cannot_manage_collaborators(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            ItineraryCollaboration.objects.filter(pk=self.collab.pk).exists()
        )

    def test_stranger_cannot_change_role(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.patch(
            self.detail_url, {'role': 'admin'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_gets_401(self):
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unknown_collaborator_returns_404(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'{self.list_url}99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_add_owner_as_collaborator(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url, {'user': self.owner.id, 'role': 'viewer'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_add_same_collaborator_twice(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url, {'user': self.member.id, 'role': 'editor'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ItineraryQueryEfficiencyTests(APITestCase):
    """The number of queries must not grow with the amount of data."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='queryuser', email='q@test.com',
            password='TestPassword123!'
        )
        self.client.force_authenticate(user=self.user)
        self.itinerary = Itinerary.objects.create(
            title='Big Trip', owner=self.user,
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 30)
        )

    def _add_items(self, count, offset=0):
        for i in range(count):
            dest = Destination.objects.create(
                name=f'Place {offset + i}', country='Land',
                description='d', category='city', price_range='budget'
            )
            ItineraryItem.objects.create(
                itinerary=self.itinerary, destination=dest,
                day_number=offset + i + 1
            )

    def _count_queries(self, url):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return len(ctx)

    def test_detail_query_count_does_not_grow_with_items(self):
        url = f'/api/v1/itineraries/{self.itinerary.id}/'
        self._add_items(1)
        few = self._count_queries(url)

        self._add_items(8, offset=1)
        many = self._count_queries(url)

        self.assertEqual(few, many)

    def test_list_query_count_does_not_grow_with_itineraries(self):
        url = '/api/v1/itineraries/'
        few = self._count_queries(url)

        for n in range(6):
            Itinerary.objects.create(
                title=f'Extra {n}', owner=self.user,
                start_date=date(2026, 11, 1), end_date=date(2026, 11, 2)
            )
        many = self._count_queries(url)

        self.assertEqual(few, many)

    def test_items_endpoint_query_count_does_not_grow(self):
        url = f'/api/v1/itineraries/{self.itinerary.id}/items/'
        self._add_items(1)
        few = self._count_queries(url)

        self._add_items(8, offset=1)
        many = self._count_queries(url)

        self.assertEqual(few, many)

    def test_public_endpoint_query_count_does_not_grow(self):
        self.itinerary.is_public = True
        self.itinerary.save()
        url = '/api/v1/itineraries/public/'
        self._add_items(1)
        few = self._count_queries(url)

        self._add_items(8, offset=1)
        many = self._count_queries(url)

        self.assertEqual(few, many)


class TripSearchAndExportTests(APITestCase):
    """Cover trip_search FBV and export_pdf action."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='search_user',
            email='search@test.com',
            password='pass12345'
        )
        self.other = User.objects.create_user(
            username='search_other',
            email='search2@test.com',
            password='pass12345'
        )
        self.dest = Destination.objects.create(
            name='Lisbon', country='Portugal',
            description='Hills', category='city', price_range='moderate'
        )
        self.trip = Itinerary.objects.create(
            owner=self.user, title='Lisbon Weekend',
            description='Short city break',
            start_date=date(2026, 11, 5), end_date=date(2026, 11, 8),
            status='planned', is_public=True
        )
        ItineraryItem.objects.create(
            itinerary=self.trip, destination=self.dest, day_number=1
        )
        self.client.force_authenticate(user=self.user)

    def test_trip_search_get(self):
        response = self.client.get('/api/v1/itineraries/search/?q=Lisbon')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_trip_search_filter_status(self):
        response = self.client.get(
            '/api/v1/itineraries/search/?status=planned')
        self.assertEqual(response.status_code, 200)

    def test_trip_search_save_preferences(self):
        response = self.client.post(
            '/api/v1/itineraries/search/',
            {'q': 'Lisbon', 'status': 'planned'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIn('last_trip_search', self.user.travel_preferences)

    def test_export_pdf(self):
        response = self.client.get(
            f'/api/v1/itineraries/{self.trip.id}/export-pdf/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_export_pdf_denied_for_other_user_private(self):
        private = Itinerary.objects.create(
            owner=self.user, title='Secret',
            start_date=date(2026, 12, 1), end_date=date(2026, 12, 3),
            is_public=False
        )
        self.client.force_authenticate(user=self.other)
        response = self.client.get(
            f'/api/v1/itineraries/{private.id}/export-pdf/'
        )
        self.assertIn(response.status_code, (403, 404))
