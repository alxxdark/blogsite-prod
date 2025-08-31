# blogs/signals.py
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from .models import Profile, Blog


def full_url(path: str) -> str:
    return f"{settings.SITE_DOMAIN.rstrip('/')}{path}"


# --- USER PROFILE SYNC (tek receiver yeterli) ---
@receiver(post_save, sender=get_user_model())
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # Profile ilişkisi varsa senkron tut
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        # Profile one-to-one ise .profile mevcut değilse erişim hata verebilir; korumalı yap
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)


# --- BLOG YAYINLANDIĞINDA E-POSTA ---
@receiver(post_save, sender=Blog)
def notify_users_on_new_post(sender, instance, created, **kwargs):
    if not created:
        return

    post_url = full_url(instance.get_absolute_url())
    subject = f"Yeni Yazı Yayında: {instance.title}"
    snippet = (getattr(instance, "short_description", "") or getattr(instance, "content", "") or "")[:160]
    message = f"{snippet}...\nDevamını oku: {post_url}"

    User = get_user_model()
    recipients = list(
        User.objects.filter(is_active=True)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
        .exclude(email__icontains="example.com")
        .values_list("email", flat=True)
    )

    print("[MAIL DEBUG] FROM=", settings.DEFAULT_FROM_EMAIL,
          "HOST=", settings.EMAIL_HOST,
          "PORT=", settings.EMAIL_PORT,
          "TLS=", settings.EMAIL_USE_TLS,
          "USER=", settings.EMAIL_HOST_USER,
          "RECIPIENTS=", recipients)

    if recipients:
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
            print("[MAIL DEBUG] send_mail OK")
        except Exception as e:
            print("[MAIL ERROR]", repr(e))


# --- PROD İÇİN TEK SEFERLİK SUPERUSER OLUŞTURMA (ENV bayraklı) ---
@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    """
    AUTO_CREATE_SUPERUSER=1 ise, admin yoksa oluşturur.
    Production’da tek seferlik kullan; iş bitince ENV'leri kaldır.
    """
    import os

    if os.environ.get("AUTO_CREATE_SUPERUSER") != "1":
        return

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if not password:
        print(">> Superuser oluşturulmadı: DJANGO_SUPERUSER_PASSWORD yok.")
        return

    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f">> Superuser oluşturuldu: {username} ✅")
    else:
        print(f">> Superuser zaten var: {username} ❗")
