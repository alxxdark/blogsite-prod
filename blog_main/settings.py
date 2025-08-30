# settings.py — Render + Postgres (Supabase/Neon) + Cloudinary (MEDIA) uyumlu

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Güvenlik / Temel ---
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-(14y1-e0z@dfg@mc(&*9xnaxe!(jpa3+tp@khmj92!3x$+$@%b"
)
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Render domain(ler)i + isteğe bağlı özel domain
_extra_hosts = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]
ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"] + _extra_hosts

# CSRF: wildcard kullanma; tam hostları ekle
CSRF_TRUSTED_ORIGINS = []
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_render_host}")

SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "").strip().rstrip("/")
if SITE_DOMAIN.startswith("http"):
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

    # Proje
    "blogs.apps.BlogsConfig",
    "assignments.apps.AssignmentsConfig",

    # 3rd party
    "crispy_forms",
    "crispy_bootstrap4",
    "whitenoise.runserver_nostatic",
]

# Cloudinary ENV varsa app’leri ekle (sırası: cloudinary, cloudinary_storage)
if os.getenv("CLOUDINARY_URL"):
    INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]

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

# --- Veritabanı (Supabase/Neon veya fallback SQLite) ---
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
DB_POOLED = os.environ.get("DB_POOLED", "").strip().lower() in {"1", "true", "yes"}

if DATABASE_URL:
    # Pooled endpoint (Supabase 6543 veya Neon -pooler) için conn_max_age=0 + server-side cursor kapalı
    conn_max_age = 0 if DB_POOLED else 600
    db_cfg = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=conn_max_age,
        ssl_require=True
    )
    db_cfg.setdefault("OPTIONS", {})
    db_cfg["OPTIONS"]["sslmode"] = "require"
    DATABASES = {"default": db_cfg}

    if DB_POOLED:
        # Pgbouncer uyumu
        DISABLE_SERVER_SIDE_CURSORS = True
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
_static_dir = BASE_DIR / "blog_main" / "static"
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []

# Django 5+ STORAGES (STATIC + MEDIA)
if DEBUG:
    _static_backend = "whitenoise.storage.CompressedStaticFilesStorage"
else:
    _static_backend = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    MEDIA_URL = "/media/"      # sembolik; gerçek URL Cloudinary tarafında
    CLOUDINARY_SECURE = True
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "staticfiles": {"BACKEND": _static_backend},
    "default": {"BACKEND": DEFAULT_FILE_STORAGE},
}

# --- Email (opsiyonel ENV'lerle) ---
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
