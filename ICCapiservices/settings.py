
from pathlib import Path
import os
from decouple import config
from datetime import timedelta

# Jazzmin settings
from django.conf import settings
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

DEBUG_ENV = config('DEBUG_ENV', default=False, cast=bool)

if DEBUG_ENV:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
    CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:8000', 'http://127.0.0.1:8000']
else:
    ALLOWED_HOSTS = ['web-production-7d611.up.railway.app',"innovationscybercafe.com", "www.innovationscybercafe.com"]
    CSRF_TRUSTED_ORIGINS = [
        'https://web-production-7d611.up.railway.app',
        'https://innovationscybercafe.com',
        'https://www.innovationscybercafe.com'
    ]
    # Production security settings for Railway
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = False  # Railway handles SSL termination
    USE_TZ = True

# Application definition

INSTALLED_APPS = [
    'channels',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'services',
    'emails',
    'payments',
    'ICCapp',
    'authentication',
    'whatsappAPI',
    'notifications',
    'customers',
    'blog',
    'CBTpractice',
    'products',
    'vidoes',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'corsheaders',
    'ckeditor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "relative_paths": False,
    "DISPLAY_OPERATION_ID": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
}



AUTH_USER_MODEL = 'authentication.CustomUser'

CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = 'ICCapiservices.urls'

PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')

SITE_DOMAIN = config('SITE_DOMAIN', default='http://localhost:8000')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            "builtins": ["ICCapp.templatetags.customtags"], # <- HERE
        },
    },
]

# WSGI_APPLICATION = 'ICCapiservices.wsgi.application'
ASGI_APPLICATION = 'ICCapiservices.asgi.application'

if DEBUG_ENV:
    CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [(config('REDIS_URL', default='redis://'))],
            },
        },
    }


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if DEBUG_ENV:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': "railway",
            'USER': "postgres",
            'PASSWORD': config('PASSWORD'),
            'HOST': config('HOST'),
            'PORT': config('PORT'),
        }
    }



import dj_database_url
db_from_env=dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

if DEBUG_ENV:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    MEDIA_URL= '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
    AWS_S3_CUSTOM_DOMAIN='%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS={'CacheControl':'max-age=86400'}
    AWS_S3_REGION_NAME = 'us-east-1'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE='ICCapiservices.storages.MediaStore'
    AWS_LOCATION = 'static'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets"),]
    STATIC_URL='https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN,AWS_LOCATION)
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


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
    'default': {
        'height': '300px',
        'width': '100%',
        'toolbar': [
            ['Format', 'Font', 'FontSize', 'TextColor', 'BGColor'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Maximize'],
            ['Source', 'Undo', 'Redo']
        ],
        'font_size': '12px',
        'colorButton_colors': '000000,ffffff'
    }
}

DJANGO_IMAGE_URL = config('DJANGO_IMAGE_URL', default='http://127.0.0.1:8000')
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024

# whatsappAPI settings
WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_FROM_PHONE_NUMBER_ID = config('WHATSAPP_PHONENUMBER_ID')
WHATSAPP_VERSION = config('WHATSAPP_VERSION')
WHATSAPP_WEBHOOK_TOKEN = config('TOKEN')


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),      # Access token valid for 7 days
    'REFRESH_TOKEN_LIFETIME': timedelta(weeks=4),    # Refresh token valid for 4 weeks
    'ROTATE_REFRESH_TOKENS': True,                   # Generate new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': True,               # Blacklist old refresh tokens
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}


 # Firebase Settings
FIREBASE_TYPE = config("FIREBASE_TYPE", "service_account")
FIREBASE_PROJECT_ID = config("FIREBASE_PROJECT_ID", "your-project-id")
FIREBASE_PRIVATE_KEY_ID = config("FIREBASE_PRIVATE_KEY_ID", "your-private-key-id")
# Fix private key formatting by replacing literal \n with actual newlines
_firebase_private_key = config("FIREBASE_PRIVATE_KEY", "your-private-key")
FIREBASE_PRIVATE_KEY = _firebase_private_key.replace('\\n', '\n') if isinstance(_firebase_private_key, str) else _firebase_private_key
FIREBASE_CLIENT_EMAIL = config("FIREBASE_CLIENT_EMAIL", "your-client-email")
FIREBASE_CLIENT_ID = config("FIREBASE_CLIENT_ID", "your-client-id")
FIREBASE_AUTH_URI = config("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
FIREBASE_TOKEN_URI = config("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
FIREBASE_AUTH_PROVIDER_X509_CERT_URL = config("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
FIREBASE_CLIENT_X509_CERT_URL = config("FIREBASE_CLIENT_X509_CERT_URL", "your-client-cert-url")
FIREBASE_UNIVERSE_DOMAIN = config("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
