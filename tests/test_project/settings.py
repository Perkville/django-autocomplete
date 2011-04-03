import os

PROJECT_DIR = os.path.dirname(__file__)
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/autocomplete.db'

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'test_project.urls'

INSTALLED_APPS = (
    'django.contrib.auth', 
    'django.contrib.contenttypes', 
    'django.contrib.sessions', 
    'django.contrib.sites',
    'django.contrib.admin',
    'test_project.testapp',
)

ADMIN_MEDIA_PREFIX = '/media/admin/'
AUTOCOMPLETE_MEDIA_PREFIX = '/media/autocomplete/'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

