from pathlib import Path
import os
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

DEBUG_ENV = config("DEBUG_ENV", default=False, cast=bool)

if DEBUG_ENV:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]
else:
    ALLOWED_HOSTS = [
        "web-production-7d611.up.railway.app",
        "innovationscybercafe.com",
        "www.innovationscybercafe.com",
    ]

# Application definition

INSTALLED_APPS = [
    "channels",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "services",
    "emails",
    "payments",
    "ICCapp",
    "authentication",
    "whatsappAPI",
    "notifications",
    "customers",
    "blog",
    "CBTpractice",
    "products",
    "vidoes",
    "ninja_extra",
    "ninja_jwt.token_blacklist",
    "ninja_jwt",
    "corsheaders",
    "ckeditor",
]


NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", default="")
GITHUB_CLIENT_ID = config("GITHUB_CLIENT_ID", default="")
GITHUB_CLIENT_SECRET = config("GITHUB_CLIENT_SECRET", default="")
REDIRECT_URI = config("REDIRECT_URI", default="http://localhost:8000/api/auth/callback")

AUTHLIB_OAUTH_CLIENTS = {
    'google': {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'access_token_url': 'https://oauth2.googleapis.com/token',
        'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
        'client_kwargs': {
            'scope': 'openid email profile'
        },
    },
    'github': {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'api_base_url': 'https://api.github.com/',
        'client_kwargs': {
            'scope': 'user:email'
        }
    }
}

AUTH_USER_MODEL = "authentication.CustomUser"

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "ICCapiservices.urls"

PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY")

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

# WSGI_APPLICATION = 'ICCapiservices.wsgi.application'
ASGI_APPLICATION = "ICCapiservices.asgi.application"

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    }
}


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if DEBUG_ENV:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("NAME"),
            "USER": config("USER"),
            "PASSWORD": config("PASSWORD"),
            "HOST": config("HOST"),
            "PORT": config("PORT"),
        }
    }


import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES["default"].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

if DEBUG_ENV:
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_S3_REGION_NAME = "us-east-1"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "ICCapiservices.storages.MediaStore"
    AWS_LOCATION = "static"
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "assets"),
    ]
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Jazzmin settings
from django.conf import settings

JAZZMIN_SETTINGS = {
    "site_title": "Innovation CyberCafe",
    "site_header": "Innovation CyberCafe",
    "welcome_sign": "Welcome to Innovation CyberCafe",
    "copyright": "ICC",
    "search_model": settings.AUTH_USER_MODEL,
    "user_avatar": "avatar",
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {
            "name": "Support",
            "url": "https://www.google.com",
            "new_window": True,
            "icon": "fas fa-life-ring",
        },
        {"model": settings.AUTH_USER_MODEL},
    ],
    "show_ui_builder": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "show_collapse": False,
    "open_my_account": False,
    "default_collapse": False,
}


CKEDITOR_CONFIGS = {
    "default": {
        "height": "300px",
        "width": "100%",
        "toolbar": [
            ["Format", "Font", "FontSize", "TextColor", "BGColor"],
            ["JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock"],
            ["Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript"],
            ["Image", "Table", "HorizontalRule", "SpecialChar"],
            ["Maximize"],
            ["Source", "Undo", "Redo"],
        ],
        "font_size": "12px",
        "colorButton_colors": "000000,ffffff",
    }
}

DJANGO_IMAGE_URL = config("DJANGO_IMAGE_URL", default="http://127.0.0.1:8000")
SITE_DOMAIN = config("SITE_DOMAIN", default="http://127.0.0.1:3000")


# whatsappAPI settings
WHATSAPP_ACCESS_TOKEN = config("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_FROM_PHONE_NUMBER_ID = config("WHATSAPP_PHONENUMBER_ID")
WHATSAPP_VERSION = config("WHATSAPP_VERSION")
WHATSAPP_WEBHOOK_TOKEN = config("TOKEN")
