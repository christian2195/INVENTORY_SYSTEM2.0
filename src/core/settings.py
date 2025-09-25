import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(BASE_DIR, 'apps')
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p4&h+vmu3(ufv16=2bfiwwx1tl#ki_9l!&$6qmcc26s)_b8@-o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'import_export',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    
# Third-party apps
    'rest_framework',
    
    # My apps - Usa la configuración explícita para cada una
    'apps.dashboard.apps.DashboardConfig',
    'apps.inventory.apps.InventoryConfig',
    'apps.movements.apps.MovementsConfig',
    'apps.dispatch_notes.apps.DispatchNotesConfig',
    'apps.quotations.apps.QuotationsConfig',
    'apps.reception_notes.apps.ReceptionNotesConfig',
    'apps.returns.apps.ReturnsConfig',
    'apps.users.apps.UsersConfig',
    'apps.orders.apps.OrdersConfig', 
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,  'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_db',
        'USER': 'admin',
        'PASSWORD': 'securepassword',
        'HOST': 'db',
        'PORT': 5432,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Configuración para Nginx
STATIC_URL = '/static/'
STATIC_ROOT = '/app/static'  # Debe coincidir con el alias en Nginx

MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

# Para cabeceras seguras detrás de proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Configuración para crispy-forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

JAZZMIN_SETTINGS = {
    "site_header": "Sistema de Inventario",
    "site_brand": "Vehiclucia",
    "site_logo": "img/logo.png", # Puedes usar tu propio logo
    "welcome_sign": "¡Bienvenido al Panel de Administración!",
    "search_model": ["auth.User", "inventory.Product"],

    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Soporte", "url": "https://github.com/farkins/django-jazzmin/issues", "new_window": True},
    ],

    "usermenu_links": [
        {"model": "auth.user"},
    ],

    "show_ui_builder": True,

    "order_with_respect_to": ["inventory", "reception_notes", "dispatch_notes", "returns"],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "inventory.product": "fas fa-box",
        "inventory.supplier": "fas fa-truck-loading",
        "inventory.client": "fas fa-handshake",
        "reception_notes.receptionnote": "fas fa-truck-loading",
        "dispatch_notes.dispatchnote": "fas fa-dolly-flatbed",
        "returns.returnnote": "fas fa-undo",
    },
}