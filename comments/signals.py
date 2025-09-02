from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from .moderation import moderate_text

@receiver(post_save, sender=Comment)
def auto_moderate_comment(sender, instance, created, **kwargs):
    if created and not instance.is_approved:
        verdict = moderate_text(instance.text)
        instance.is_approved = verdict["approve"]
        instance.is_flagged = not verdict["approve"]
        instance.mod_score = verdict["score"]
        instance.mod_signals = verdict["signals"]
        instance.save()
