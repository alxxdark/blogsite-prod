from django.db import models
from django.contrib.auth import get_user_model
from blogs.models import Blog

User = get_user_model()

class Comment(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=100, blank=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    # Moderasyon alanları
    is_approved = models.BooleanField(default=False)
    is_flagged  = models.BooleanField(default=False)
    mod_score   = models.FloatField(default=0.0)
    mod_signals = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.author_name or self.user} - {self.text[:30]}"
