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


class BookingCancelAndRoleTests(APITestCase):
    """The cancel action and per-action permissions."""

    def setUp(self):
        make = User.objects.create_user
        self.owner = make('bcowner', 'bco@test.com', 'testpass123')
        self.other = make('bcother', 'bcot@test.com', 'testpass123')
        self.role_admin = make(
            'bcadmin', 'bca@test.com', 'testpass123', role='admin'
        )

        self.itinerary = Itinerary.objects.create(
            owner=self.owner, title='Cancel Trip',
            start_date=date.today(), end_date=date.today()
        )
        self.booking = Booking.objects.create(
            itinerary=self.itinerary, booked_by=self.owner,
            reference_number='CXL-001', cost='100.00',
            booking_date=date.today()
        )
        self.cancel_url = f'/api/v1/bookings/{self.booking.id}/cancel/'

    def test_owner_can_cancel_pending_booking(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.cancel_url)

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')

    def test_cancelling_a_paid_booking_marks_it_refunded(self):
        self.booking.status = 'confirmed'
        self.booking.payment_status = 'paid'
        self.booking.save()
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.cancel_url)

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'refunded')

    def test_cannot_cancel_twice(self):
        self.client.force_authenticate(user=self.owner)
        self.client.post(self.cancel_url)

        response = self.client.post(self.cancel_url)

        self.assertEqual(response.status_code, 400)

    def test_cannot_cancel_completed_booking(self):
        self.booking.status = 'completed'
        self.booking.save()
        self.client.force_authenticate(user=self.owner)

        self.assertEqual(self.client.post(self.cancel_url).status_code, 400)

    def test_other_user_cannot_cancel(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.post(self.cancel_url)

        self.assertEqual(response.status_code, 404)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'pending')

    def test_anonymous_cannot_cancel(self):
        self.assertEqual(self.client.post(self.cancel_url).status_code, 401)

    def test_admin_role_sees_all_bookings(self):
        self.client.force_authenticate(user=self.role_admin)

        response = self.client.get('/api/v1/bookings/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_regular_user_only_sees_own_bookings(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.get('/api/v1/bookings/')

        self.assertEqual(len(response.data['results']), 0)

    def test_get_permissions_differs_per_action(self):
        from bookings.views import BookingViewSet
        from bookings.permissions import IsBookingOwnerOrAdmin

        view = BookingViewSet()
        view.action = 'list'
        self.assertEqual(len(view.get_permissions()), 1)

        view.action = 'cancel'
        kinds = [type(p) for p in view.get_permissions()]
        self.assertIn(IsBookingOwnerOrAdmin, kinds)


class AccommodationActivityAPITests(APITestCase):
    """Cover Accommodation / Activity endpoints and model helpers."""

    def setUp(self):
        from destinations.models import Destination
        from bookings.models import Accommodation, Activity

        self.user = User.objects.create_user(
            username='acc_user', email='acc@test.com', password='pass12345'
        )
        self.dest = Destination.objects.create(
            name='Cape Town', country='South Africa',
            description='Coastal city', category='city', price_range='moderate'
        )
        self.acc = Accommodation.objects.create(
            name='Waterfront Hotel', destination=self.dest,
            accommodation_type='hotel', price_per_night='120.00', max_guests=2
        )
        self.act = Activity.objects.create(
            name='Table Mountain Hike', destination=self.dest,
            category='outdoor', price='50.00', duration_hours='3.0'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_accommodations(self):
        response = self.client.get('/api/v1/bookings/accommodations/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertTrue(any(r['name'] == 'Waterfront Hotel' for r in results))

    def test_list_activities(self):
        response = self.client.get('/api/v1/bookings/activities/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertTrue(
            any(r['name'] == 'Table Mountain Hike' for r in results))

    def test_filter_accommodations_by_destination(self):
        response = self.client.get(
            f'/api/v1/bookings/accommodations/?destination={self.dest.id}'
        )
        self.assertEqual(response.status_code, 200)

    def test_accommodation_str(self):
        self.assertIn('Waterfront Hotel', str(self.acc))

    def test_activity_str(self):
        self.assertIn('Table Mountain Hike', str(self.act))


class BulkUpdateBookingsTests(APITestCase):
    """Cover POST /api/v1/bookings/bulk-update/."""

    def setUp(self):
        from itineraries.models import Itinerary
        from bookings.models import Booking

        self.owner = User.objects.create_user(
            username='bulk_owner', email='bulk@test.com', password='pass12345'
        )
        self.other = User.objects.create_user(
            username='bulk_other', email='bulk2@test.com', password='pass12345'
        )
        self.itinerary = Itinerary.objects.create(
            owner=self.owner, title='Bulk Trip',
            start_date='2026-10-01', end_date='2026-10-05'
        )
        self.b1 = Booking.objects.create(
            booked_by=self.owner, itinerary=self.itinerary,
            reference_number='BULK-001', status='pending',
            cost='100.00', booking_date='2026-09-01'
        )
        self.b2 = Booking.objects.create(
            booked_by=self.owner, itinerary=self.itinerary,
            reference_number='BULK-002', status='pending',
            cost='200.00', booking_date='2026-09-01'
        )
        self.url = '/api/v1/bookings/bulk-update/'

    def test_bulk_update_status_success(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.url, {
            'booking_ids': [self.b1.id, self.b2.id],
            'status': 'confirmed',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success_count'], 2)
        self.b1.refresh_from_db()
        self.assertEqual(self.b1.status, 'confirmed')

    def test_bulk_update_rejects_empty_ids(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.url, {
            'booking_ids': [],
            'status': 'confirmed',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_bulk_update_rejects_invalid_status(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.url, {
            'booking_ids': [self.b1.id],
            'status': 'not-a-status',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_bulk_update_requires_status_or_payment(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.url, {
            'booking_ids': [self.b1.id],
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_bulk_update_skips_other_users_bookings(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(self.url, {
            'booking_ids': [self.b1.id],
            'status': 'confirmed',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['failure_count'], 1)
        self.b1.refresh_from_db()
        self.assertEqual(self.b1.status, 'pending')

    def test_bulk_update_payment_status(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.url, {
            'booking_ids': [self.b1.id],
            'payment_status': 'paid',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.b1.refresh_from_db()
        self.assertEqual(self.b1.payment_status, 'paid')


class ActivityLogAPITests(APITestCase):
    def setUp(self):
        from bookings.models import ActivityLog
        self.user = User.objects.create_user(
            username='log_user', email='log@test.com', password='pass12345'
        )
        self.other = User.objects.create_user(
            username='log_other', email='log2@test.com', password='pass12345'
        )
        ActivityLog.objects.create(
            user=self.user, action='book', entity_type='booking',
            entity_id=1, description='test log'
        )
        ActivityLog.objects.create(
            user=self.other, action='cancel', entity_type='booking',
            entity_id=2, description='other log'
        )

    def test_user_sees_only_own_logs(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/bookings/logs/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertTrue(all(
            r.get('username') == 'log_user' or r.get('user') for r in results
        ))
        self.assertEqual(len(results), 1)
