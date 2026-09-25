from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Destination
from reviews.models import Review


User = get_user_model()


class DestinationPermissionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='TestPassword123!'
        )

        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='TestPassword123!',
            is_staff=True
        )

        self.destination = Destination.objects.create(
            name='Cape Town',
            country='South Africa',
            city='Cape Town',
            description='A beautiful coastal city.',
            category='city',
            price_range='moderate',
            created_by=self.admin
        )

        self.url = '/api/v1/destinations/'
        self.detail_url = f'{self.url}{self.destination.id}/'

    def test_normal_user_can_read_destinations(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_normal_user_cannot_create_destination(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'name': 'Durban',
                'country': 'South Africa',
                'city': 'Durban',
                'description': 'A coastal city.',
                'category': 'city',
                'price_range': 'moderate',
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_create_destination(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.url,
            {
                'name': 'Durban',
                'country': 'South Africa',
                'city': 'Durban',
                'description': 'A coastal city.',
                'category': 'city',
                'price_range': 'moderate',
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        destination = Destination.objects.get(
            name='Durban'
        )

        self.assertEqual(
            destination.created_by,
            self.admin
        )

    def test_normal_user_cannot_update_destination(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.detail_url,
            {'name': 'Updated Cape Town'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_update_destination(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_url,
            {'name': 'Updated Cape Town'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_normal_user_cannot_delete_destination(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_delete_destination(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )


class DestinationFunctionalityTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='destinationuser',
            email='destination@test.com',
            password='testpass123'
        )

        self.destination = Destination.objects.create(
            name='Cape Town',
            country='South Africa',
            description='A beautiful coastal city.',
            category='City',
            price_range='$$',
            created_by=self.user
        )

        self.url = '/api/v1/destinations/'

    def test_user_can_list_destinations(self):
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
            response.data['results'][0]['name'],
            'Cape Town'
        )

        self.assertEqual(
            response.data['results'][0]['country'],
            'South Africa'
        )

    def test_user_can_retrieve_destination(self):
        self.client.force_authenticate(user=self.user)

        url = f'{self.url}{self.destination.id}/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['name'],
            'Cape Town'
        )

        self.assertEqual(
            response.data['country'],
            'South Africa'
        )

        self.assertEqual(
            response.data['description'],
            'A beautiful coastal city.'
        )

    def test_admin_can_create_destination(self):
        self.admin = User.objects.create_user(
            username='destinationadmin',
            email='destinationadmin@test.com',
            password='adminpass123',
            is_staff=True
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.url,
            {
                'name': 'Kruger National Park',
                'country': 'South Africa',
                'description': 'A famous wildlife destination.',
                'category': 'city',
                'price_range': 'moderate'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Destination.objects.filter(
                name='Kruger National Park'
            ).exists()
        )

        destination = Destination.objects.get(
            name='Kruger National Park'
        )

        self.assertEqual(
            destination.country,
            'South Africa'
        )

        self.assertEqual(
            destination.created_by,
            self.admin
        )

    def test_admin_update_changes_destination(self):
        admin = User.objects.create_user(
            username='updateadmin',
            email='updateadmin@test.com',
            password='adminpass123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        url = f'{self.url}{self.destination.id}/'

        response = self.client.patch(
            url,
            {
                'name': 'Updated Cape Town'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.destination.refresh_from_db()

        self.assertEqual(
            self.destination.name,
            'Updated Cape Town'
        )

    def test_admin_delete_removes_destination(self):
        admin = User.objects.create_user(
            username='deleteadmin',
            email='deleteadmin@test.com',
            password='adminpass123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        url = f'{self.url}{self.destination.id}/'

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Destination.objects.filter(
                id=self.destination.id
            ).exists()
        )

    def test_user_can_filter_destinations_by_country(self):
        Destination.objects.create(
            name='Durban',
            country='South Africa',
            description='A coastal city.',
            category='city',
            price_range='moderate',
            created_by=self.user
        )

        Destination.objects.create(
            name='Paris',
            country='France',
            description='A famous European city.',
            category='city',
            price_range='expensive',
            created_by=self.user
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            self.url,
            {'country': 'South Africa'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            2
        )

        for destination in response.data['results']:
            self.assertEqual(
                destination['country'],
                'South Africa'
            )

    def test_user_can_search_destinations(self):
        Destination.objects.create(
            name='Kruger National Park',
            country='South Africa',
            description='A famous wildlife destination.',
            category='nature',
            price_range='moderate',
            created_by=self.user
        )

        Destination.objects.create(
            name='Paris',
            country='France',
            description='A famous European city.',
            category='city',
            price_range='expensive',
            created_by=self.user
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            self.url,
            {'search': 'Kruger'}
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
            response.data['results'][0]['name'],
            'Kruger National Park'
        )

    def test_user_can_order_destinations_by_name(self):
        Destination.objects.create(
            name='Durban',
            country='South Africa',
            description='A coastal city.',
            category='city',
            price_range='moderate',
            created_by=self.user
        )

        Destination.objects.create(
            name='Johannesburg',
            country='South Africa',
            description='A major South African city.',
            category='city',
            price_range='moderate',
            created_by=self.user
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            self.url,
            {'ordering': 'name'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        names = [
            destination['name']
            for destination in response.data['results']
        ]

        self.assertEqual(
            names,
            [
                'Cape Town',
                'Durban',
                'Johannesburg'
            ]
        )

    def test_user_can_get_top_rated_destinations(self):
        destination_2 = Destination.objects.create(
            name='Kruger National Park',
            country='South Africa',
            description='A famous wildlife destination.',
            category='nature',
            price_range='moderate',
            created_by=self.user
        )

        destination_3 = Destination.objects.create(
            name='Durban',
            country='South Africa',
            description='A coastal city.',
            category='city',
            price_range='moderate',
            created_by=self.user
        )

        Review.objects.create(
            destination=self.destination,
            reviewer=self.user,
            rating=4,
            comment='Great destination.'
        )

        other_user = User.objects.create_user(
            username='reviewer2',
            email='reviewer2@test.com',
            password='testpass123'
        )

        Review.objects.create(
            destination=destination_2,
            reviewer=other_user,
            rating=5,
            comment='Excellent destination.'
        )

        Review.objects.create(
            destination=destination_3,
            reviewer=other_user,
            rating=3,
            comment='It was okay.'
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'{self.url}top_rated/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data[0]['name'],
            'Kruger National Park'
        )