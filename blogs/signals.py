# blogs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Blog

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

@receiver(post_save, sender=Blog)
def notify_users_on_new_post(sender, instance, created, **kwargs):
    if created:
        subject = f"Yeni Yazı Yayında: {instance.title}"
        message = (
            f"{instance.short_description[:100]}...\n"
            f"Devamını oku: https://blogsite-prod.onrender.com/posts/{instance.slug}/"
        )

        # Emaili olan tüm kullanıcılar
        recipient_list = list(User.objects.exclude(email="").values_list("email", flat=True))

        if recipient_list:  # En az bir e-posta varsa
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # Güvenli kullanım
                recipient_list,
                fail_silently=False
            )
