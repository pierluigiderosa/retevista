"""
Django settings for retevista project.

Generated by 'django-admin startproject' using Django 1.11.18.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from decouple import config
import socket


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# SECURITY WARNING: don't run with debug turned on in production!
if socket.gethostname()=='pierluigi-Lenovo-U41-70' or socket.gethostname()=='pierluigi-ThinkCentre-M710q':
    DEBUG = True
else:
    DEBUG=False
#DEBUG=True

ALLOWED_HOSTS = ['127.0.0.1','www.onegis.it','onegis.it']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.postgres',
    'django_tables2',
    'django_filters',
    'bootstrap_modal_forms',
    'djgeojson',
    'leaflet',
    'widget_tweaks',
    'crispy_forms',
    'django_cron',
    'income',
    'consiglio',
    'dash_aziende',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'retevista.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'retevista.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/


LANGUAGE_CODE = 'it-it'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]
#STATIC_ROOT = os.path.join(BASE_DIR, "static/")



#email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = True


CRON_CLASSES = [
    #
    # 'income.cron.MyCronJob22'
    "income.cron.get_data",
    "income.cron.aggregate_data",
    "income.cron.do_bilancio",
    "income.cron.get_forecast",
]

DJANGO_CRON_LOCKFILE_PATH = [
    "/tmp",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#login

LOGIN_URL = '/retevista/accounts/login/'
LOGOUT_REDIRECT_URL = '/retevista'


SERIALIZATION_MODULES = {
     "geojson": "django.contrib.gis.serializers.geojson",
  }

LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (9,38, 15,44),
    'DEFAULT_CENTER': (42.90,12.0),
    'DEFAULT_ZOOM': 7,
    'MIN_ZOOM': 1,
    'MAX_ZOOM': 23,
    'TILES': [
        ('Esri Word Topo', 'http://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x} ', {'attribution': '&copy; Esri'}),
        ('Wikimedia', 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png ', {
            'attribution': '&copy; <a href="http://www.openstreetmap.org/copyright/">OpenStreetMap</a> contributors, under ODbL '}),

        ('Stamen', 'http://a.tile.stamen.com/terrain/{z}/{x}/{y}.png', {'attribution': '&copy; Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap', 'maxZoom': 22}),

    ],
    'OVERLAYS': [
        ('Mapbox satellite',
         'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA ',
         {'attribution': '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a>'})
    ],
    'ATTRIBUTION_PREFIX': 'Powered by <a href="https://www.onegis.it/">onegis</a>',
    'MINIMAP': False,
}


CRISPY_TEMPLATE_PACK = 'bootstrap4'