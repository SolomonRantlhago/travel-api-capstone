from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from itineraries.models import Itinerary
from bookings.models import Booking


User = get_user_model()


class BookingObjectPermissionTests(APITestCase):

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

        self.itinerary = Itinerary.objects.create(
            owner=self.owner,
            title='Test Itinerary',
            description='Test itinerary description',
            start_date=date.today(),
            end_date=date.today()
        )

        self.booking = Booking.objects.create(
            booked_by=self.owner,
            itinerary=self.itinerary,
            reference_number='BOOK-001',
            status='pending',
            cost=1000.00,
            booking_date=date.today()
        )

        self.url = f'/api/v1/bookings/{self.booking.id}/'

    def test_owner_can_view_booking(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_owner_can_update_booking(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.url,
            {'status': 'confirmed'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_owner_can_delete_booking(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)

    def test_other_user_cannot_view_booking(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_update_booking(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.url,
            {'status': 'confirmed'},
            format='json'
        )

        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_booking(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 404)

    def test_admin_can_view_booking(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_update_booking(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.url,
            {'status': 'confirmed'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_can_delete_booking(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)


class BookingConfirmPermissionTests(APITestCase):

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

        self.itinerary = Itinerary.objects.create(
            owner=self.owner,
            title='Test Itinerary',
            description='Test itinerary description',
            start_date=date.today(),
            end_date=date.today()
        )

        self.booking = Booking.objects.create(
            booked_by=self.owner,
            itinerary=self.itinerary,
            reference_number='BOOK-001',
            status='pending',
            cost=1000.00,
            booking_date=date.today()
        )

        self.url = (
            f'/api/v1/bookings/'
            f'{self.booking.id}/confirm/'
        )

    def test_owner_can_confirm_booking(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            'confirmed'
        )

    def test_other_user_cannot_confirm_booking(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)

    def test_admin_can_confirm_booking(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            'confirmed'
        )
class BookingFunctionalityTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='bookinguser',
            email='bookinguser@test.com',
            password='testpass123'
        )

        self.itinerary = Itinerary.objects.create(
            owner=self.user,
            title='Cape Town Trip',
            description='Trip to Cape Town.',
            start_date=date.today(),
            end_date=date.today()
        )

        self.url = '/api/v1/bookings/'

    def test_user_can_create_booking(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'itinerary': self.itinerary.id,
                'reference_number': 'BOOK-002',
                'status': 'pending',
                'cost': '1500.00',
                'booking_date': str(date.today())
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            201
        )

        booking = Booking.objects.get(
            reference_number='BOOK-002'
        )

        self.assertEqual(
            booking.booked_by,
            self.user
        )

        self.assertEqual(
            booking.itinerary,
            self.itinerary
        )

        self.assertEqual(
            booking.cost,
            1500
        )

    def test_user_can_list_own_bookings(self):
        Booking.objects.create(
            booked_by=self.user,
            itinerary=self.itinerary,
            reference_number='BOOK-003',
            status='pending',
            cost=2000.00,
            booking_date=date.today()
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['count'],
            1
        )

        self.assertEqual(
            response.data['results'][0]['reference_number'],
            'BOOK-003'
        )
    def test_user_only_sees_own_bookings(self):
        other_user = User.objects.create_user(
            username='otherbookinguser',
            email='otherbooking@test.com',
            password='testpass123'
        )

        other_itinerary = Itinerary.objects.create(
            owner=other_user,
            title='Other User Trip',
            description="Other user's itinerary.",
            start_date=date.today(),
            end_date=date.today()
        )

        Booking.objects.create(
            booked_by=other_user,
            itinerary=other_itinerary,
            reference_number='BOOK-OTHER',
            status='pending',
            cost=3000.00,
            booking_date=date.today()
        )

        Booking.objects.create(
            booked_by=self.user,
            itinerary=self.itinerary,
            reference_number='BOOK-MINE',
            status='pending',
            cost=1500.00,
            booking_date=date.today()
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['count'],
            1
        )

        self.assertEqual(
            response.data['results'][0]['reference_number'],
            'BOOK-MINE'
        )
    def test_user_can_retrieve_booking(self):
        booking = Booking.objects.create(
            booked_by=self.user,
            itinerary=self.itinerary,
            reference_number='BOOK-004',
            status='pending',
            cost=2500.00,
            booking_date=date.today()
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/bookings/{booking.id}/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['reference_number'],
            'BOOK-004'
        )

        self.assertEqual(
            response.data['status'],
            'pending'
        )

        self.assertEqual(
            response.data['cost'],
            '2500.00'
        )
    def test_user_can_update_booking(self):
        booking = Booking.objects.create(
            booked_by=self.user,
            itinerary=self.itinerary,
            reference_number='BOOK-005',
            status='pending',
            cost=1800.00,
            booking_date=date.today()
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/bookings/{booking.id}/'

        response = self.client.patch(
            url,
            {
                'status': 'confirmed'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        booking.refresh_from_db()

        self.assertEqual(
            booking.status,
            'confirmed'
        )
    def test_user_can_delete_booking(self):
        booking = Booking.objects.create(
            booked_by=self.user,
            itinerary=self.itinerary,
            reference_number='BOOK-006',
            status='pending',
            cost=1200.00,
            booking_date=date.today()
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/bookings/{booking.id}/'

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            204
        )

        self.assertFalse(
            Booking.objects.filter(
                id=booking.id
            ).exists()
        )
    def test_cannot_confirm_already_confirmed_booking(self):
        booking = Booking.objects.create(
            booked_by=self.user,
            itinerary=self.itinerary,
            reference_number='BOOK-007',
            status='confirmed',
            cost=2000.00,
            booking_date=date.today()
        )
    
        self.client.force_authenticate(user=self.user)
    
        url = f'/api/v1/bookings/{booking.id}/confirm/'
    
        response = self.client.post(url)
    
        self.assertEqual(
            response.status_code,
            400
        )
    
        self.assertEqual(
            response.data['detail'],
            "Booking is already 'confirmed', cannot confirm."
        )
    def test_unauthenticated_user_cannot_confirm_booking(self):
        booking = Booking.objects.create(
            booked_by=self.user,
            itinerary=self.itinerary,
            reference_number='BOOK-008',
            status='pending',
            cost=2200.00,
            booking_date=date.today()
        )
    
        url = f'/api/v1/bookings/{booking.id}/confirm/'
    
        response = self.client.post(url)
    
        self.assertEqual(
            response.status_code,
            401
        )