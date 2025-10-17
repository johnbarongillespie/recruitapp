# recruitapp_core/settings.py

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE') == 'True'
DEBUG = DEVELOPMENT_MODE

ALLOWED_HOSTS_STRING = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = ALLOWED_HOSTS_STRING.split(',')

INSTALLED_APPS = [
    'recruiting',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'whitenoise.runserver_nostatic',  <-- THIS LINE HAS BEEN REMOVED
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add WhiteNoise only in production
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'recruitapp_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'recruitapp_core.wsgi.application'

IS_BUILD_PROCESS = os.environ.get('IS_BUILD_PROCESS') == 'true'
if IS_BUILD_PROCESS:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
else:
    # Use custom backend with DNS retry logic for Render cold starts
    db_config = dj_database_url.config(conn_max_age=600, ssl_require=not DEVELOPMENT_MODE)
    db_config['ENGINE'] = 'recruiting.db_backends'  # Custom PostgreSQL wrapper with DNS retry
    db_config['CONN_MAX_AGE'] = 600  # Keep connections alive for 10 minutes
    DATABASES = {'default': db_config}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'  # US Central Time
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'recruiting' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = '/setup/role/'  # Redirect to role selection after login
LOGOUT_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allauth signup redirect
ACCOUNT_SIGNUP_REDIRECT_URL = '/setup/role/'  # Redirect to role selection after signup

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# =============================================================================
# DJANGO ALLAUTH CONFIGURATION
# =============================================================================

# Email and Login Configuration
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Optional for now, can be 'mandatory' later
ACCOUNT_UNIQUE_EMAIL = True  # Each email can only be used once
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

# Login methods (new format)
ACCOUNT_LOGIN_METHODS = {'email'}  # Login with email instead of username

# Signup fields (new format - requires username, email, email2 confirmation, and passwords)
ACCOUNT_SIGNUP_FIELDS = ['username*', 'email*', 'email2*', 'password1*', 'password2*']

# Custom signup form with profanity filter and email validation
ACCOUNT_FORMS = {
    'signup': 'recruiting.forms.CustomSignupForm',
}

# Social Account Settings (Google OAuth)
SOCIALACCOUNT_AUTO_SIGNUP = True  # Auto-create account from Google
SOCIALACCOUNT_EMAIL_REQUIRED = True  # Require email from social providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', ''),
            'key': ''
        }
    }
}

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'