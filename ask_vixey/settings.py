"""
Django settings for ask_vixey project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '5!wtbo@pl1f(9)#874ma=k1@s++7&g&i)qdo6r4ty*4wpm1b!4'

DEBUG =  False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ask',
    'djangosphinx',
    'debug_toolbar',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ('127.0.0.1',)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': '608400',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ask_db',
        'USER': 'ask',
        'PASSWORD': 'ask_pass',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

ROOT_URLCONF = 'ask_vixey.urls'
WSGI_APPLICATION = 'ask_vixey.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/'
STATIC_ROOT = '/var/www/ask_vixey/static/'

MEDIA_URL = '/uploads/'
MEDIA_ROOT = '/var/www/ask_vixey/uploads/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

SPHINX_API_VERSION = 0x116

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = '25'
EMAIL_HOST_USER = 'postbot@aithelle.com'
EMAIL_HOST_PASSWORD = '***' ###
EMAIL_USE_TLS = True


TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', ('django.template.loaders.filesystem.Loader',
 'django.template.loaders.app_directories.Loader')),
)