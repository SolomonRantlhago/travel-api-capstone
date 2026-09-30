"""Project-level tests: settings, exception handler and API docs."""
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from travel_api.exceptions import custom_exception_handler


class SettingsTests(SimpleTestCase):

    def test_static_and_media_roots_are_configured(self):
        self.assertTrue(str(settings.STATIC_ROOT).endswith('staticfiles'))
        self.assertTrue(settings.MEDIA_ROOT)

    def test_tests_do_not_write_into_the_real_media_folder(self):
        self.assertNotEqual(
            str(settings.MEDIA_ROOT),
            str(settings.BASE_DIR / 'media')
        )

    def test_custom_exception_handler_is_registered(self):
        self.assertEqual(
            settings.REST_FRAMEWORK['EXCEPTION_HANDLER'],
            'travel_api.exceptions.custom_exception_handler'
        )


class ExceptionHandlerTests(SimpleTestCase):

    def test_django_validation_error_becomes_400(self):
        response = custom_exception_handler(
            DjangoValidationError(['Something is wrong.']), {}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], ['Something is wrong.'])

    def test_integrity_error_becomes_409(self):
        response = custom_exception_handler(IntegrityError(), {})

        self.assertEqual(response.status_code, 409)

    def test_other_exceptions_fall_through_to_drf(self):
        # An unknown exception is not handled -> None (re-raised by DRF)
        self.assertIsNone(custom_exception_handler(RuntimeError('x'), {}))


class ApiDocumentationTests(APITestCase):

    def test_swagger_ui_is_public(self):
        self.assertEqual(self.client.get('/api/docs/').status_code, 200)

    def test_redoc_is_public(self):
        self.assertEqual(self.client.get('/api/redoc/').status_code, 200)

    def test_schema_documents_the_new_and_fixed_endpoints(self):
        response = self.client.get('/api/schema/?format=json')

        self.assertEqual(response.status_code, 200)
        paths = response.json()['paths']
        self.assertIn('/api/v1/itineraries/{id}/status/', paths)
        self.assertIn(
            '/api/v1/itineraries/{itinerary_id}/collaborators/{user_id}/',
            paths
        )
        self.assertIn('/api/v1/bookings/{id}/cancel/', paths)
