from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author_name", "user", "is_approved", "is_flagged", "created")
    list_filter = ("is_approved", "is_flagged", "created")
    search_fields = ("text", "author_name", "user__username")
    ordering = ("-created",)
