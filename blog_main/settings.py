import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(14y1-e0z@dfg@mc(&*9xnaxe!(jpa3+tp@khmj92!3x$+$@%b'
DEBUG = True
ALLOWED_HOSTS = ['.onrender.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "cloudinary",
    "cloudinary_storage",
    'assignments',
    'crispy_forms',
    'crispy_bootstrap4',
    'blogs.apps.BlogsConfig',
    'dashboards',

    # Media (Cloudinary)
    'cloudinary',
    'cloudinary_storage',
]

SITE_DOMAIN = "https://blogsite-prod.onrender.com"  # sondaki / yok

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog_main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blogs.context_processors.get_categories',
                'blogs.context_processors.get_social_links',
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_main.wsgi.application'

# DATABASES
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'blog_main' / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
if CLOUDINARY_URL:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    # MEDIA_URL Cloudinary tarafından otomatik verilir, burada sembolik dursa yeter
    MEDIA_URL = "/media/"
else:
    # Lokal geliştirme için
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# ========= EMAIL SETTINGS =========
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')                       # örn: smtp.gmail.com
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')             # örn: alisagnak4607@gmail.com
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')     # Gmail App Password vb.

# Gönderen adresi: login adresiyle aynı tut (Gmail için önemli)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or '')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', EMAIL_HOST_USER or '')
EMAIL_SUBJECT_PREFIX = "[Blogend] "
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', 20))

# (İsteğe bağlı) Bildirim alıcısı fallback
NOTIFY_DEFAULT_RECIPIENTS = os.environ.get('NOTIFY_DEFAULT_RECIPIENTS', 'alisagnak4607@gmail.com').split(',')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
