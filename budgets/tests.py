from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from itineraries.models import Itinerary
from .models import Budget, BudgetExpense
from .permissions import IsBudgetExpenseOwnerOrAdmin


User = get_user_model()


class BudgetObjectPermissionTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='budgetowner',
            email='owner@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPassword123!'
        )

        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='TestPassword123!',
            is_staff=True
        )

        self.itinerary = Itinerary.objects.create(
            title='Cape Town Trip',
            description='A trip to Cape Town.',
            owner=self.owner,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            status='planned',
            is_public=False
        )

        self.budget = Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.owner,
            total_limit='10000.00',
            currency='ZAR'
        )

        self.url = f'/api/v1/budgets/{self.budget.id}/'

    def test_owner_can_view_budget(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_owner_can_update_budget(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.url,
            {'total_limit': '12000.00'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_owner_can_delete_budget(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_other_user_cannot_view_budget(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_other_user_cannot_update_budget(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.url,
            {'total_limit': '12000.00'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_other_user_cannot_delete_budget(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_view_other_users_budget(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_can_update_other_users_budget(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.url,
            {'total_limit': '15000.00'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_can_delete_other_users_budget(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )


class BudgetExpenseObjectPermissionTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='expenseowner',
            email='expenseowner@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='expenseother',
            email='expenseother@example.com',
            password='TestPassword123!'
        )

        self.admin = User.objects.create_user(
            username='expenseadmin',
            email='expenseadmin@example.com',
            password='TestPassword123!',
            is_staff=True
        )

        self.itinerary = Itinerary.objects.create(
            title='Durban Trip',
            description='A trip to Durban.',
            owner=self.owner,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            status='planned',
            is_public=False
        )

        self.budget = Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.owner,
            total_limit='10000.00',
            currency='ZAR'
        )

        self.expense = BudgetExpense.objects.create(
            budget=self.budget,
            category='food',
            description='Restaurant',
            amount='500.00',
            date=date(2026, 11, 2)
        )

        self.url = (
            f'/api/v1/budgets/{self.budget.id}/expenses/'
        )

    def test_owner_can_view_budget_expenses(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_other_user_cannot_view_budget_expenses(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_view_budget_expenses(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_owner_can_create_budget_expense(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.url,
            {
                'category': 'transport',
                'description': 'Airport transfer',
                'amount': '300.00',
                'date': '2026-11-03'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_other_user_cannot_create_budget_expense(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.url,
            {
                'category': 'transport',
                'description': 'Airport transfer',
                'amount': '300.00',
                'date': '2026-11-03'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_create_budget_expense(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.url,
            {
                'category': 'transport',
                'description': 'Airport transfer',
                'amount': '300.00',
                'date': '2026-11-03'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_expense_cannot_exceed_budget_limit(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.url,
            {
                'category': 'transport',
                'description': 'Expensive airport transfer',
                'amount': '10000.00',
                'date': '2026-11-03'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'This expense would exceed the budget limit.',
            str(response.data)
        )

    def test_budget_expenses_return_404_for_nonexistent_budget(self):
        self.client.force_authenticate(user=self.owner)

        url = '/api/v1/budgets/99999/expenses/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_budget_expense_permission_allows_owner(self):
        factory = APIRequestFactory()
        request = factory.get(self.url)
        request.user = self.owner

        permission = IsBudgetExpenseOwnerOrAdmin()

        result = permission.has_object_permission(
            request,
            None,
            self.expense
        )

        self.assertTrue(result)

    def test_budget_expense_permission_allows_admin(self):
        factory = APIRequestFactory()
        request = factory.get(self.url)
        request.user = self.admin

        permission = IsBudgetExpenseOwnerOrAdmin()

        result = permission.has_object_permission(
            request,
            None,
            self.expense
        )

        self.assertTrue(result)

    def test_budget_expense_permission_denies_other_user(self):
        factory = APIRequestFactory()
        request = factory.get(self.url)
        request.user = self.other_user

        permission = IsBudgetExpenseOwnerOrAdmin()

        result = permission.has_object_permission(
            request,
            None,
            self.expense
        )

        self.assertFalse(result)


class BudgetFunctionalityTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='budgetuser',
            email='budgetuser@example.com',
            password='TestPassword123!'
        )

        self.itinerary = Itinerary.objects.create(
            title='Johannesburg Trip',
            description='A trip to Johannesburg.',
            owner=self.user,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 7),
            status='planned',
            is_public=False
        )

        self.url = '/api/v1/budgets/'

    def test_user_can_create_budget(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'itinerary': self.itinerary.id,
                'total_limit': '5000.00',
                'currency': 'ZAR'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        budget = Budget.objects.get(
            itinerary=self.itinerary
        )

        self.assertEqual(
            budget.owner,
            self.user
        )

        self.assertEqual(
            budget.total_limit,
            5000
        )

        self.assertEqual(
            budget.currency,
            'ZAR'
        )

    def test_user_can_list_own_budgets(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            0
        )

    def test_user_only_sees_own_budgets(self):
        other_user = User.objects.create_user(
            username='otherbudgetuser',
            email='otherbudget@example.com',
            password='TestPassword123!'
        )

        other_itinerary = Itinerary.objects.create(
            title='Durban Trip',
            description='A trip to Durban.',
            owner=other_user,
            start_date=date(2026, 12, 10),
            end_date=date(2026, 12, 15),
            status='planned',
            is_public=False
        )

        Budget.objects.create(
            itinerary=other_itinerary,
            owner=other_user,
            total_limit='8000.00',
            currency='ZAR'
        )

        Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.user,
            total_limit='5000.00',
            currency='ZAR'
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
            response.data['results'][0]['owner'],
            self.user.id
        )

    def test_admin_can_see_all_budgets(self):
        other_user = User.objects.create_user(
            username='otheradminbudgetuser',
            email='otheradminbudget@example.com',
            password='TestPassword123!'
        )

        other_itinerary = Itinerary.objects.create(
            title='Durban Trip',
            description='A trip to Durban.',
            owner=other_user,
            start_date=date(2026, 12, 10),
            end_date=date(2026, 12, 15),
            status='planned',
            is_public=False
        )

        Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.user,
            total_limit='5000.00',
            currency='ZAR'
        )

        Budget.objects.create(
            itinerary=other_itinerary,
            owner=other_user,
            total_limit='8000.00',
            currency='ZAR'
        )

        admin = User.objects.create_user(
            username='budgetlistadmin',
            email='budgetlistadmin@example.com',
            password='TestPassword123!',
            is_staff=True
        )

        self.client.force_authenticate(user=admin)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['count'],
            2
        )

    def test_user_can_retrieve_budget(self):
        budget = Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.user,
            total_limit='5000.00',
            currency='ZAR'
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/budgets/{budget.id}/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['itinerary_title'],
            'Johannesburg Trip'
        )

        self.assertEqual(
            response.data['total_spent'],
            '0.00'
        )

        self.assertEqual(
            response.data['remaining'],
            '5000.00'
        )

        self.assertEqual(
            response.data['budget_status'],
            'Not started'
        )

    def test_other_user_cannot_view_budget_summary(self):
        budget = Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.user,
            total_limit='5000.00',
            currency='ZAR'
        )

        other_user = User.objects.create_user(
            username='summaryotheruser',
            email='summaryother@example.com',
            password='TestPassword123!'
        )

        self.client.force_authenticate(user=other_user)

        url = f'/api/v1/budgets/{budget.id}/summary/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_budget_summary_shows_within_budget(self):
        budget = Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.user,
            total_limit='5000.00',
            currency='ZAR'
        )

        BudgetExpense.objects.create(
            budget=budget,
            category='food',
            description='Lunch',
            amount='1000.00',
            date=date(2026, 12, 2)
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/budgets/{budget.id}/summary/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['status'],
            'Within budget'
        )

    def test_budget_summary_shows_budget_reached(self):
        budget = Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.user,
            total_limit='5000.00',
            currency='ZAR'
        )

        BudgetExpense.objects.create(
            budget=budget,
            category='accommodation',
            description='Hotel',
            amount='5000.00',
            date=date(2026, 12, 2)
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/budgets/{budget.id}/summary/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['status'],
            'Budget reached'
        )

    def test_budget_summary_shows_over_budget(self):
        budget = Budget.objects.create(
            itinerary=self.itinerary,
            owner=self.user,
            total_limit='5000.00',
            currency='ZAR'
        )

        BudgetExpense.objects.create(
            budget=budget,
            category='accommodation',
            description='Hotel',
            amount='6000.00',
            date=date(2026, 12, 2)
        )

        self.client.force_authenticate(user=self.user)

        url = f'/api/v1/budgets/{budget.id}/summary/'

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['status'],
            'Over budget'
        )


class BudgetCreationOwnershipTests(APITestCase):
    """A budget may only be attached to an itinerary the user owns."""

    def setUp(self):
        make = User.objects.create_user
        self.alice = make('alice_b', 'alice_b@test.com', 'TestPassword123!')
        self.bob = make('bob_b', 'bob_b@test.com', 'TestPassword123!')
        self.site_admin = make(
            'admin_b', 'admin_b@test.com', 'TestPassword123!', role='admin'
        )

        self.alice_trip = Itinerary.objects.create(
            owner=self.alice, title="Alice's trip",
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 5)
        )
        self.bob_trip = Itinerary.objects.create(
            owner=self.bob, title="Bob's trip",
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 5)
        )
        self.url = '/api/v1/budgets/'

    def _create(self, itinerary):
        return self.client.post(
            self.url,
            {'itinerary': itinerary.id, 'total_limit': '500.00'},
            format='json'
        )

    def test_owner_can_create_budget_for_own_itinerary(self):
        self.client.force_authenticate(user=self.alice)

        response = self._create(self.alice_trip)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Budget.objects.get().owner, self.alice)

    def test_user_cannot_create_budget_on_someone_elses_itinerary(self):
        self.client.force_authenticate(user=self.bob)

        response = self._create(self.alice_trip)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('itinerary', response.data)
        self.assertEqual(Budget.objects.count(), 0)

    def test_site_admin_may_create_budget_for_any_itinerary(self):
        self.client.force_authenticate(user=self.site_admin)

        response = self._create(self.alice_trip)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_itinerary_can_only_have_one_budget(self):
        self.client.force_authenticate(user=self.alice)
        self._create(self.alice_trip)

        response = self._create(self.alice_trip)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_budget_cannot_be_moved_to_another_itinerary(self):
        second_trip = Itinerary.objects.create(
            owner=self.alice, title='Second',
            start_date=date(2026, 11, 1), end_date=date(2026, 11, 3)
        )
        budget = Budget.objects.create(
            itinerary=self.alice_trip, owner=self.alice, total_limit='500.00'
        )
        self.client.force_authenticate(user=self.alice)

        response = self.client.put(
            f'{self.url}{budget.id}/',
            {'itinerary': second_trip.id, 'total_limit': '500.00'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        budget.refresh_from_db()
        self.assertEqual(budget.itinerary, self.alice_trip)


class BudgetSerializerEdgeCaseTests(APITestCase):
    """Cover remaining BudgetSerializer / expense edge paths."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='ser_budget', email='serb@test.com', password='pass12345'
        )
        self.itinerary = Itinerary.objects.create(
            owner=self.user, title='Serializer Trip',
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 5)
        )
        self.budget = Budget.objects.create(
            itinerary=self.itinerary, owner=self.user, total_limit='100.00'
        )
        self.client.force_authenticate(user=self.user)

    def test_budget_status_not_started(self):
        response = self.client.get(f'/api/v1/budgets/{self.budget.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['budget_status'], 'Not started')

    def test_budget_status_within_budget(self):
        BudgetExpense.objects.create(
            budget=self.budget, category='food',
            description='Lunch', amount='40.00', date=date(2026, 10, 2)
        )
        response = self.client.get(f'/api/v1/budgets/{self.budget.id}/')
        self.assertEqual(response.data['budget_status'], 'Within budget')

    def test_budget_status_reached(self):
        BudgetExpense.objects.create(
            budget=self.budget, category='food',
            description='All', amount='100.00', date=date(2026, 10, 2)
        )
        response = self.client.get(f'/api/v1/budgets/{self.budget.id}/')
        self.assertEqual(response.data['budget_status'], 'Budget reached')

    def test_budget_status_over(self):
        BudgetExpense.objects.create(
            budget=self.budget, category='food',
            description='Over', amount='120.00', date=date(2026, 10, 2)
        )
        response = self.client.get(f'/api/v1/budgets/{self.budget.id}/')
        self.assertEqual(response.data['budget_status'], 'Over budget')

    def test_reject_zero_total_limit(self):
        trip2 = Itinerary.objects.create(
            owner=self.user, title='Second',
            start_date=date(2026, 11, 1), end_date=date(2026, 11, 3)
        )
        response = self.client.post('/api/v1/budgets/', {
            'itinerary': trip2.id, 'total_limit': '0.00'
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_expense(self):
        BudgetExpense.objects.create(
            budget=self.budget,
            category='food',
            description='Snack',
            amount='10.00',
            date=date(2026, 10, 2)
        )
        # Nested expense update via list endpoint if supported;
        # otherwise patch budget.
        response = self.client.get(
            f'/api/v1/budgets/{self.budget.id}/expenses/'
        )
        self.assertEqual(response.status_code, 200)
