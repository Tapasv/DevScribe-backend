from pathlib import Path
import os
from datetime import timedelta
import dj_database_url

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# =====================================================
# BASE DIR
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# SECURITY
# =====================================================

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only")

DEBUG = os.environ.get("DEBUG", "False") == "True"


# =====================================================
# HOSTS
# =====================================================

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "devscribe-backend-a4ot.onrender.com",
]


# =====================================================
# APPS
# =====================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    
    # Cloudinary
    "cloudinary_storage",
    "cloudinary",

    "blog",
]


# =====================================================
# MIDDLEWARE (ORDER MATTERS)
# =====================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =====================================================
# URLS / WSGI
# =====================================================

ROOT_URLCONF = "backend.urls"
WSGI_APPLICATION = "backend.wsgi.application"


# =====================================================
# TEMPLATES
# =====================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =====================================================
# DATABASE
# =====================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Production or connecting to remote PostgreSQL
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=False,  # Allow external connections
        )
    }
else:
    # Local development with SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =====================================================
# I18N
# =====================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# =====================================================
# STATIC FILES
# =====================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# =====================================================
# CLOUDINARY CONFIGURATION
# =====================================================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'di2ayzev4'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '625397468435941'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'FGpSjwU1DwP3-jEAGrj7siuPfzA'),
}

# Use Cloudinary for media files
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'


# =====================================================
# REST
# =====================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


# =====================================================
# JWT
# =====================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# =====================================================
# CORS / CSRF
# =====================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://dev-scribe-frontend.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://dev-scribe-frontend.vercel.app",
    "https://devscribe-backend-a4ot.onrender.com",
]


# =====================================================
# RENDER HTTPS FIX (CRITICAL)
# =====================================================

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Only enable SSL redirect in production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"