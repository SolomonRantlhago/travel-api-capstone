"""
Settings used when running the test suite.

Inherits everything from the main settings and overrides the parts that
make tests slow or that would write into the real project folders:

* a fast (insecure) password hasher - tests create many users
* a throw-away MEDIA_ROOT so uploaded test files never touch ./media
* no HTTPS redirect, and in-memory e-mail delivery
"""
import atexit
import shutil
import tempfile

from .settings import *  # noqa: F401,F403

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

MEDIA_ROOT = tempfile.mkdtemp(prefix='travel_api_test_media_')
atexit.register(shutil.rmtree, MEDIA_ROOT, ignore_errors=True)

SECURE_SSL_REDIRECT = False
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    },
}
