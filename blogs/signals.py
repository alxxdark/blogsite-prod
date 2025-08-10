# blogs/signals.py
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Blog, Profile

def full_url(path: str) -> str:
    return f"{settings.SITE_DOMAIN.rstrip('/')}{path}"

@receiver(post_save, sender=Blog)
def notify_users_on_new_post(sender, instance, created, **kwargs):
    if not created:
        return

    post_url = full_url(reverse("post_detail", kwargs={"slug": instance.slug}))
    subject = f"Yeni Yazı Yayında: {instance.title}"
    snippet = (instance.short_description or instance.content or "")[:160]
    message = f"{snippet}...\nDevamını oku: {post_url}"

    recipients = list(
        User.objects
        .filter(is_active=True)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
        .exclude(email__icontains="example.com")  # hatalı placeholder’ları filtrele
        .values_list("email", flat=True)
    )
    if recipients:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
