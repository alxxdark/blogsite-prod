from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Blog

def full_url(path: str) -> str:
    return f"{settings.SITE_DOMAIN.rstrip('/')}{path}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@receiver(post_save, sender=Blog)
def notify_users_on_new_post(sender, instance, created, **kwargs):
    if not created:
        return

    post_url = full_url(instance.get_absolute_url())
    subject = f"Yeni Yazı Yayında: {instance.title}"
    snippet = (getattr(instance, "short_description", "") or getattr(instance, "content", "") or "")[:160]
    message = f"{snippet}...\nDevamını oku: {post_url}"

    recipients = list(
        User.objects.filter(is_active=True)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
        .exclude(email__icontains="example.com")  # placeholderları ele
        .values_list("email", flat=True)
    )
    if recipients:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)

    print("[MAIL DEBUG]", settings.DEFAULT_FROM_EMAIL, recipients)
