from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from destinations.models import Destination
from reviews.models import Review


User = get_user_model()


class ReviewPermissionTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )

        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True
        )

        self.destination = Destination.objects.create(
            name='Cape Town',
            country='South Africa',
            description='A beautiful destination.',
            category='city',
            price_range='moderate'
        )

        self.review = Review.objects.create(
            destination=self.destination,
            reviewer=self.owner,
            rating=5,
            comment='Excellent destination!'
        )

        self.url = f'/api/v1/reviews/{self.review.id}/'


    def test_anyone_can_view_review(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


    def test_authenticated_user_can_create_review(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            '/api/v1/reviews/',
            {
                'destination': self.destination.id,
                'rating': 4,
                'comment': 'Very good!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)


    def test_unauthenticated_user_cannot_create_review(self):
        response = self.client.post(
            '/api/v1/reviews/',
            {
                'destination': self.destination.id,
                'rating': 4,
                'comment': 'Very good!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)


    def test_owner_can_update_review(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.url,
            {'rating': 4},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_update_review_saves_changes(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.url,
            {
                'rating': 4,
                'comment': 'Updated review!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.review.refresh_from_db()

        self.assertEqual(self.review.rating, 4)
        self.assertEqual(
            self.review.comment,
            'Updated review!'
        )


    def test_other_user_cannot_update_review(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.url,
            {'rating': 4},
            format='json'
        )

        self.assertEqual(response.status_code, 403)


    def test_admin_can_update_review(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.url,
            {'rating': 4},
            format='json'
        )

        self.assertEqual(response.status_code, 200)


    def test_owner_can_delete_review(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)


    def test_other_user_cannot_delete_review(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 403)


    def test_admin_can_delete_review(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)
    def test_create_review_saves_correct_data(self):
            self.client.force_authenticate(user=self.other_user)
        
            response = self.client.post(
                '/api/v1/reviews/',
                {
                    'destination': self.destination.id,
                    'rating': 4,
                    'comment': 'Very good!'
                },
                format='json'
            )
        
            self.assertEqual(response.status_code, 201)
        
            review = Review.objects.get(
                id=response.data['id']
            )
        
            self.assertEqual(
                review.reviewer,
                self.other_user
            )
        
            self.assertEqual(
                review.destination,
                self.destination
            )
        
            self.assertEqual(
                review.rating,
                4
            )
        
            self.assertEqual(
                review.comment,
                'Very good!'
            )
    def test_delete_review_removes_from_database(self):
        self.client.force_authenticate(user=self.owner)
    
        response = self.client.delete(self.url)
    
        self.assertEqual(response.status_code, 204)
    
        self.assertFalse(
            Review.objects.filter(
                id=self.review.id
            ).exists()
        )
    def test_create_review_rejects_invalid_rating(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            '/api/v1/reviews/',
            {
                'destination': self.destination.id,
                'rating': 6,
                'comment': 'Invalid rating'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        
    def test_unauthenticated_user_cannot_update_review(self):
        response = self.client.patch(
            self.url,
            {'rating': 4},
            format='json'
        )

        self.assertEqual(response.status_code, 401)

class MyReviewsPermissionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )

        self.destination1 = Destination.objects.create(
            name='Cape Town',
            country='South Africa',
            description='A beautiful destination.',
            category='city',
            price_range='moderate'
        )

        self.destination2 = Destination.objects.create(
            name='Durban',
            country='South Africa',
            description='A coastal destination.',
            category='beach',
            price_range='moderate'
        )

        self.user_review = Review.objects.create(
            destination=self.destination1,
            reviewer=self.user,
            rating=5,
            comment='Great!'
        )

        self.other_review = Review.objects.create(
            destination=self.destination2,
            reviewer=self.other_user,
            rating=3,
            comment='Okay.'
        )

        self.url = '/api/v1/reviews/my_reviews/'


    def test_unauthenticated_user_cannot_access_my_reviews(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)


    def test_user_only_sees_their_own_reviews(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data['results']), 1)

        self.assertEqual(
            response.data['results'][0]['id'],
            self.user_review.id
        )
    def test_my_reviews_returns_correct_review_data(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        review = response.data['results'][0]

        self.assertEqual(
            review['id'],
            self.user_review.id
        )

        self.assertEqual(
            review['rating'],
            5
        )

        self.assertEqual(
            review['comment'],
            'Great!'
        )

class DestinationReviewsPermissionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )

        self.destination = Destination.objects.create(
            name='Cape Town',
            country='South Africa',
            description='A beautiful destination.',
            category='city',
            price_range='moderate'
        )

        self.review = Review.objects.create(
            destination=self.destination,
            reviewer=self.user,
            rating=5,
            comment='Excellent!'
        )

        self.url = (
            f'/api/v1/reviews/destination/'
            f'{self.destination.id}/'
        )


    def test_anyone_can_view_destination_reviews(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


    def test_unauthenticated_user_cannot_create_destination_review(self):
        response = self.client.post(
            self.url,
            {
                'rating': 4,
                'comment': 'Very good!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)


    def test_authenticated_user_can_create_destination_review(self):
        # Use a different user because one user can only
        # review a destination once.
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            self.url,
            {
                'rating': 4,
                'comment': 'Very good!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)
    def test_create_destination_review_saves_correct_data(self):
        other_user = User.objects.create_user(
            username='other2',
            email='other2@test.com',
            password='testpass123'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            self.url,
            {
                'rating': 4,
                'comment': 'Very good!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        review = Review.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            review.destination,
            self.destination
        )

        self.assertEqual(
            review.reviewer,
            other_user
        )

        self.assertEqual(
            review.rating,
            4
        )

        self.assertEqual(
            review.comment,
            'Very good!'
        )
    def test_user_cannot_review_same_destination_twice(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'rating': 4,
                'comment': 'Another review'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
    def test_destination_reviews_only_return_selected_destination(self):
        other_destination = Destination.objects.create(
            name='Durban',
            country='South Africa',
            description='A coastal destination.',
            category='beach',
            price_range='moderate'
        )

        Review.objects.create(
            destination=other_destination,
            reviewer=self.user,
            rating=3,
            comment='Okay.'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]['id'],
            self.review.id
        )