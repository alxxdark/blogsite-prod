# blogs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .models import Blog
from django.core.mail import send_mail
from django.conf import settings

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
        message = f"{instance.short_description[:100]}...\nDevamını oku: {settings.SITE_DOMAIN}/posts/{instance.slug}/"
        recipient_list = [user.email for user in User.objects.all() if user.email]
        send_mail(subject, message, 'alisagnak4607@gmail.com', recipient_list, fail_silently=False)