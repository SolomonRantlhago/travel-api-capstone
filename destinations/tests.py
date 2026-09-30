from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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

    def test_role_admin_can_create_destination(self):
        role_admin = User.objects.create_user(
            username='roleadmin',
            email='roleadmin@example.com',
            password='TestPassword123!',
            role='admin',
            is_staff=False
        )

        self.client.force_authenticate(user=role_admin)

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
            role_admin
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

    def test_image_file_over_5mb_is_rejected(self):
        admin = User.objects.create_user(
            username='imageadmin',
            email='imageadmin@test.com',
            password='adminpass123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        large_image = SimpleUploadedFile(
            'large.jpg',
            b'a' * (5 * 1024 * 1024 + 1),
            content_type='image/jpeg'
        )

        response = self.client.post(
            self.url,
            {
                'name': 'Large Image Destination',
                'country': 'South Africa',
                'description': 'A destination with a large image.',
                'category': 'city',
                'price_range': 'moderate',
                'image': large_image,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'image',
            response.data
        )

    def test_invalid_image_type_is_rejected(self):
        admin = User.objects.create_user(
            username='invalidimageadmin',
            email='invalidimage@test.com',
            password='adminpass123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        invalid_file = SimpleUploadedFile(
            'document.txt',
            b'This is not an image.',
            content_type='text/plain'
        )

        response = self.client.post(
            self.url,
            {
                'name': 'Invalid Image Destination',
                'country': 'South Africa',
                'description': 'A destination with an invalid image.',
                'category': 'city',
                'price_range': 'moderate',
                'image': invalid_file,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'image',
            response.data
        )


class DestinationImageValidationOnWritesTests(APITestCase):
    """Image rules apply to create AND update, not only the read serializer."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='imgadmin2', email='imgadmin2@test.com',
            password='TestPassword123!', is_staff=True
        )
        self.destination = Destination.objects.create(
            name='Update Target', country='Chile', description='d',
            category='mountain', price_range='budget'
        )
        self.client.force_authenticate(user=self.admin)

    def _png(self, name='pic.png', content_type='image/png'):
        import io
        from PIL import Image

        buffer = io.BytesIO()
        Image.new('RGB', (4, 4), 'red').save(buffer, format='PNG')
        return SimpleUploadedFile(
            name, buffer.getvalue(), content_type=content_type
        )

    def test_real_png_is_accepted_on_update(self):
        response = self.client.patch(
            f'/api/v1/destinations/{self.destination.id}/',
            {'image': self._png()}, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fake_image_is_rejected_on_update(self):
        # Right name and declared type, but the bytes are not an image.
        fake = SimpleUploadedFile(
            'pic.png', b'definitely not a png', content_type='image/png'
        )

        response = self.client.patch(
            f'/api/v1/destinations/{self.destination.id}/',
            {'image': fake}, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)

    def test_oversized_image_is_rejected_on_update(self):
        big = SimpleUploadedFile(
            'big.png', b'a' * (5 * 1024 * 1024 + 1), content_type='image/png'
        )

        response = self.client.patch(
            f'/api/v1/destinations/{self.destination.id}/',
            {'image': big}, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_extension_is_rejected_on_create(self):
        response = self.client.post(
            '/api/v1/destinations/',
            {'name': 'Ext', 'country': 'X', 'description': 'd',
             'category': 'city', 'price_range': 'budget',
             'image': self._png(name='pic.gif')},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DestinationQueryEfficiencyTests(APITestCase):
    """Detail, list and top_rated must not run a query per row."""

    def setUp(self):
        from .models import Amenity, DestinationAmenity

        self.user = User.objects.create_user(
            username='qdest', email='qdest@test.com',
            password='TestPassword123!'
        )
        self.amenity = Amenity.objects.create(name='Wifi')
        self.DestinationAmenity = DestinationAmenity

    def _make(self, n):
        for i in range(n):
            dest = Destination.objects.create(
                name=f'D{Destination.objects.count()}', country='C',
                description='d', category='city', price_range='budget',
                created_by=self.user
            )
            self.DestinationAmenity.objects.create(
                destination=dest, amenity=self.amenity
            )
            Review.objects.create(
                destination=dest, reviewer=self.user, rating=5
            )

    def _queries(self, url):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return len(ctx)

    def test_list_query_count_is_constant(self):
        self._make(1)
        few = self._queries('/api/v1/destinations/')
        self._make(6)
        self.assertEqual(few, self._queries('/api/v1/destinations/'))

    def test_top_rated_query_count_is_constant(self):
        self._make(1)
        few = self._queries('/api/v1/destinations/top_rated/')
        self._make(4)
        self.assertEqual(few, self._queries('/api/v1/destinations/top_rated/'))

    def test_detail_includes_amenities_and_creator(self):
        self._make(1)
        dest = Destination.objects.get()

        response = self.client.get(f'/api/v1/destinations/{dest.id}/')

        self.assertEqual(response.data['created_by_username'], 'qdest')
        self.assertEqual(len(response.data['amenities']), 1)


class DestinationRecommendationsTests(APITestCase):
    """Cover GET /api/v1/destinations/recommendations/."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='rec_user', email='rec@test.com', password='pass12345',
            travel_preferences={
                'categories': ['beach'],
                'price_range': 'moderate',
                'countries': ['South Africa'],
            }
        )
        self.beach = Destination.objects.create(
            name='Durban Beach', country='South Africa',
            description='Warm coast', category='beach', price_range='moderate'
        )
        self.mountain = Destination.objects.create(
            name='Drakensberg', country='South Africa',
            description='Peaks', category='mountain', price_range='budget'
        )
        self.user.favorite_destinations.add(self.beach)
        self.client.force_authenticate(user=self.user)

    def test_recommendations_returns_results(self):
        response = self.client.get('/api/v1/destinations/recommendations/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('preferences_used', response.data)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_recommendations_prefers_matching_category(self):
        response = self.client.get('/api/v1/destinations/recommendations/')
        names = [r['name'] for r in response.data['results']]
        # Beach + favorite should rank at or near the top
        self.assertIn('Durban Beach', names)
