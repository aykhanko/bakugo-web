from pathlib import Path
from datetime import timedelta
import os
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv())

#########################################################

CORE_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

DOWNLOADED_APPS = []

MAIN_APPS = [
    'transport',
    'accounts',
]

INSTALLED_APPS = CORE_APPS + DOWNLOADED_APPS + MAIN_APPS

#########################################################

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


#########################################################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


#########################################################
'''DATABASE CONFIG'''

if config("DATABASE_TYPE") == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif config("DATABASE_TYPE") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("POSTGRES_NAME"),
            "USER": config("POSTGRES_USER"),
            "PASSWORD": config("POSTGRES_PASSWORD"),
            "HOST": config("POSTGRES_HOST"),
            "PORT": config("POSTGRES_PORT"),
        }
    }
#########################################################
'''VALIDATION'''

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

#########################################################
'''I18, TIME'''

from django.utils.translation import gettext_lazy as _
import os

LANGUAGE_CODE = 'en'  

USE_I18N = False    

LANGUAGES = [
    ('az', _('AZ')),
    ('ru', _('RU')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

USE_TZ = True
TIME_ZONE = 'Asia/Baku'

#########################################################
'''STATIC SETTINGS'''

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


#########################################################
'''MEDIA'''
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#########################################################

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

#########################################################
'''UNFOLD ADMIN CONFIG'''

UNFOLD = {
    "SITE_TITLE": "BakuGo Admin",
    "SITE_HEADER": "BakuGo",
    "SITE_SUBHEADER": "Public Transport Platform",
    "SITE_URL": "/",
    "SITE_SYMBOL": "directions_bus",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "17 24 39",
            "default-dark": "243 244 246",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "240 249 255",
            "100": "224 242 254",
            "200": "186 230 253",
            "300": "125 211 252",
            "400": "56 189 248",
            "500": "14 165 233",
            "600": "2 132 199",
            "700": "3 105 161",
            "800": "7 89 133",
            "900": "12 74 110",
            "950": "8 47 73",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {"title": "Dashboard", "icon": "dashboard", "link": "/admin/"},
                ],
            },
            {
                "title": "Transport",
                "separator": True,
                "items": [
                    {"title": "Routes", "icon": "route", "link": "/admin/transport/route/"},
                    {"title": "Stops", "icon": "location_on", "link": "/admin/transport/stop/"},
                    {"title": "Vehicles", "icon": "directions_bus", "link": "/admin/transport/vehicle/"},
                    {"title": "Vehicle Locations", "icon": "my_location", "link": "/admin/transport/vehiclelocation/"},
                ],
            },
            {
                "title": "Users",
                "separator": True,
                "items": [
                    {"title": "Users", "icon": "group", "link": "/admin/auth/user/"},
                    {"title": "Favorite Routes", "icon": "favorite", "link": "/admin/transport/favoriteroute/"},
                    {"title": "Favorite Stops", "icon": "star", "link": "/admin/transport/favoritestop/"},
                ],
            },
        ],
    },
}
