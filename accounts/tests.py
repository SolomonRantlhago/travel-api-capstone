from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase


User = get_user_model()


class RegistrationTests(APITestCase):

    def setUp(self):
        self.url = '/api/v1/accounts/register/'

    def test_user_can_register(self):
        response = self.client.post(
            self.url,
            {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'testpass123',
                'confirm_password': 'testpass123',
                'first_name': 'New',
                'last_name': 'User'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            User.objects.filter(
                username='newuser'
            ).exists()
        )

    def test_registration_fails_when_passwords_do_not_match(self):
        response = self.client.post(
            self.url,
            {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'testpass123',
                'confirm_password': 'different123',
                'first_name': 'New',
                'last_name': 'User'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_registration_fails_with_short_password(self):
        response = self.client.post(
            self.url,
            {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'short',
                'confirm_password': 'short',
                'first_name': 'New',
                'last_name': 'User'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_registration_does_not_store_plaintext_password(self):
        response = self.client.post(
            self.url,
            {
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'testpass123',
                'confirm_password': 'testpass123',
                'first_name': 'New',
                'last_name': 'User'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(
            username='newuser'
        )

        self.assertNotEqual(
            user.password,
            'testpass123'
        )

        self.assertTrue(
            user.check_password('testpass123')
        )


class ProfileTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@test.com',
            password='testpass123'
        )

        self.url = '/api/v1/accounts/profile/'

    def test_unauthenticated_user_cannot_access_profile(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_view_own_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['username'],
            'profileuser'
        )
        self.assertEqual(
            response.data['email'],
            'profile@test.com'
        )

    def test_authenticated_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url,
            {
                'first_name': 'Solomon',
                'last_name': 'Rantlhago',
                'bio': 'Software developer'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            'Solomon'
        )
        self.assertEqual(
            self.user.last_name,
            'Rantlhago'
        )
        self.assertEqual(
            self.user.bio,
            'Software developer'
        )

    def test_profile_id_and_created_at_are_read_only(self):
        self.client.force_authenticate(user=self.user)

        original_id = self.user.id
        original_created_at = self.user.created_at

        response = self.client.patch(
            self.url,
            {
                'id': 9999,
                'created_at': '2000-01-01T00:00:00Z'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.id,
            original_id
        )
        self.assertEqual(
            self.user.created_at,
            original_created_at
        )


class PasswordChangeTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='passworduser',
            email='password@test.com',
            password='oldpass123'
        )

        self.url = '/api/v1/accounts/password/change/'

    def test_unauthenticated_user_cannot_change_password(self):
        response = self.client.post(
            self.url,
            {
                'old_password': 'oldpass123',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_user_can_change_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'old_password': 'oldpass123',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('newpass123')
        )

        self.assertFalse(
            self.user.check_password('oldpass123')
        )

    def test_password_change_fails_with_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'old_password': 'wrongpass123',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_password_change_fails_when_passwords_do_not_match(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                'old_password': 'oldpass123',
                'new_password': 'newpass123',
                'confirm_password': 'different123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)


class PasswordResetRequestTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='resetuser',
            email='reset@test.com',
            password='oldpass123'
        )

        self.url = '/api/v1/accounts/password/reset/'

    def test_password_reset_request_with_existing_email(self):
        response = self.client.post(
            self.url,
            {
                'email': 'reset@test.com'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_password_reset_request_with_unknown_email(self):
        response = self.client.post(
            self.url,
            {
                'email': 'unknown@test.com'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_password_reset_request_with_invalid_email(self):
        response = self.client.post(
            self.url,
            {
                'email': 'not-an-email'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)


class PasswordResetConfirmTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='confirmuser',
            email='confirm@test.com',
            password='oldpass123'
        )

        self.url = '/api/v1/accounts/password/reset/confirm/'

        self.uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        self.token = default_token_generator.make_token(
            self.user
        )

    def test_password_reset_confirm_with_valid_token(self):
        response = self.client.post(
            self.url,
            {
                'uid': self.uid,
                'token': self.token,
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('newpass123')
        )

        self.assertFalse(
            self.user.check_password('oldpass123')
        )

    def test_password_reset_confirm_with_invalid_token(self):
        response = self.client.post(
            self.url,
            {
                'uid': self.uid,
                'token': 'invalid-token',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_with_mismatched_passwords(self):
        response = self.client.post(
            self.url,
            {
                'uid': self.uid,
                'token': self.token,
                'new_password': 'newpass123',
                'confirm_password': 'different123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_with_invalid_uid(self):
        response = self.client.post(
            self.url,
            {
                'uid': 'invalid-uid',
                'token': self.token,
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)


class AdminUserManagementTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            is_staff=True,
            role='admin'
        )

        self.user = User.objects.create_user(
            username='normaluser',
            email='normal@test.com',
            password='userpass123',
            role='traveler'
        )

        self.list_url = '/api/v1/accounts/users/'

        self.detail_url = (
            f'/api/v1/accounts/users/{self.user.id}/'
        )

    def test_unauthenticated_user_cannot_list_users(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 401)

    def test_normal_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

    def test_role_admin_can_list_users(self):
        role_admin = User.objects.create_user(
            username='roleadmin',
            email='roleadmin@test.com',
            password='adminpass123',
            role='admin',
            is_staff=False
        )

        self.client.force_authenticate(user=role_admin)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

    def test_normal_user_cannot_view_user_detail(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_view_user_detail(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['username'],
            'normaluser'
        )

    def test_role_admin_can_view_user_detail(self):
        role_admin = User.objects.create_user(
            username='roleadmin',
            email='roleadmin@test.com',
            password='adminpass123',
            role='admin',
            is_staff=False
        )

        self.client.force_authenticate(user=role_admin)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['username'],
            'normaluser'
        )

    def test_admin_can_update_user(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_url,
            {
                'first_name': 'Updated',
                'last_name': 'User'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            'Updated'
        )

        self.assertEqual(
            self.user.last_name,
            'User'
        )

    def test_admin_can_delete_user(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            User.objects.filter(
                username='normaluser'
            ).exists()
        )

    def test_unauthenticated_user_cannot_access_user_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 401)


class PasswordStrengthTests(APITestCase):
    """Weak passwords must be rejected with a 400, never a 500."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='strongpw',
            email='strongpw@test.com',
            password='Original-Pass-42'
        )

    def test_registration_rejects_numeric_password(self):
        response = self.client.post(
            '/api/v1/accounts/register/',
            {
                'username': 'weakling',
                'email': 'weakling@test.com',
                'password': '12345678',
                'confirm_password': '12345678',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertFalse(User.objects.filter(username='weakling').exists())

    def test_registration_rejects_password_similar_to_username(self):
        response = self.client.post(
            '/api/v1/accounts/register/',
            {
                'username': 'travelerjoe',
                'email': 'joe@test.com',
                'password': 'travelerjoe',
                'confirm_password': 'travelerjoe',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_password_change_rejects_weak_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/v1/accounts/password/change/',
            {
                'old_password': 'Original-Pass-42',
                'new_password': '12345678',
                'confirm_password': '12345678',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Original-Pass-42'))

    def test_password_reset_confirm_rejects_weak_password(self):
        response = self.client.post(
            '/api/v1/accounts/password/reset/confirm/',
            {
                'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
                'token': default_token_generator.make_token(self.user),
                'new_password': '12345678',
                'confirm_password': '12345678',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)


class UserModelTests(APITestCase):

    def test_is_site_admin_true_for_admin_role_staff_and_superuser(self):
        admin_role = User.objects.create_user(
            'roleadmin', 'ra@test.com', 'Pass-word-123', role='admin'
        )
        staff = User.objects.create_user(
            'staffer', 'st@test.com', 'Pass-word-123', is_staff=True
        )
        superuser = User.objects.create_superuser(
            'super', 'su@test.com', 'Pass-word-123'
        )

        self.assertTrue(admin_role.is_site_admin)
        self.assertTrue(staff.is_site_admin)
        self.assertTrue(superuser.is_site_admin)

    def test_is_site_admin_false_for_regular_traveler(self):
        traveler = User.objects.create_user(
            'plain', 'plain@test.com', 'Pass-word-123'
        )

        self.assertFalse(traveler.is_site_admin)
