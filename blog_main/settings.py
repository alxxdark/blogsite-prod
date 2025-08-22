# settings.py — Render uyumlu + Cloudinary (yalnızca MEDIA)

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Güvenlik / Temel ---
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-(14y1-e0z@dfg@mc(&*9xnaxe!(jpa3+tp@khmj92!3x$+$@%b"
)
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Render domain(ler)i
_extra_hosts = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]
ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"] + _extra_hosts

SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "https://blogsite-prod.onrender.com").rstrip("/")

CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]
if SITE_DOMAIN.startswith("http"):
    from urllib.parse import urlparse
    _host = urlparse(SITE_DOMAIN).netloc
    if _host:
        CSRF_TRUSTED_ORIGINS.append(f"https://{_host}")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# --- Uygulamalar ---
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd party
    "crispy_forms",
    "crispy_bootstrap4",
    "whitenoise.runserver_nostatic",
]

# Cloudinary (opsiyonel) — ENV varsa app’leri ekle
if os.getenv("CLOUDINARY_URL"):
    INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]

CRISPY_TEMPLATE_PACK = "bootstrap4"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "blog_main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blogs.context_processors.get_categories",
                "blogs.context_processors.get_social_links",
            ],
        },
    },
]

WSGI_APPLICATION = "blog_main.wsgi.application"

# --- Veritabanı ---
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Şifre doğrulama ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N ---
LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

# --- Statik (WhiteNoise) ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "blog_main" / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Medya (Cloudinary varsa orayı kullan, yoksa local) ---
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
if CLOUDINARY_URL:
    # Sadece MEDIA Cloudinary'de; STATIC yine WhiteNoise
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    MEDIA_URL = "/media/"  # sembolik; gerçek URL Cloudinary tarafında üretilir
    # (İsteğe bağlı) Cloudinary için güvenli URL tercihleri:
    CLOUDINARY_SECURE = True
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# --- Email ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", EMAIL_HOST_USER or "")
EMAIL_SUBJECT_PREFIX = "[Blogsite] "
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", 20))

NOTIFY_DEFAULT_RECIPIENTS = os.environ.get(
    "NOTIFY_DEFAULT_RECIPIENTS", "alisagnak4607@gmail.com"
).split(",")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Logging (özet) ---
LOGGING = {
    "version": 1, 
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO" if not DEBUG else "DEBUG"},
}
