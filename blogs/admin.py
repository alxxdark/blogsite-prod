from django.contrib import admin
from django.contrib.admin.sites import NotRegistered

from .models import (
    Category,
    Blog,
    Comment,
    Profile,
    CommentStatus,
    ContactMessage,
    # StaticPage  # aşağıda try/except ile ele alacağız
)

# -----------------------------
# Category
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name", "created_at")
    search_fields = ("category_name",)


# -----------------------------
# Blog
# -----------------------------
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title", "category", "author", "status", "is_featured", "updated_at")
    list_filter = ("status", "is_featured", ("updated_at", admin.DateFieldListFilter))
    search_fields = ("id", "title", "category__category_name", "status")
    list_editable = ("is_featured",)


# -----------------------------
# Comment
# -----------------------------
# Güvenli unregister: daha önce admin.site.register(Comment) ile kayıtlandıysa temizle
try:
    admin.site.unregister(Comment)
except NotRegistered:
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "blog", "user", "short", "status", "toxicity", "sentiment", "is_spam", "created_at")
    list_filter = ("status", "is_spam", ("created_at", admin.DateFieldListFilter))
    search_fields = ("comment", "user__username", "blog__title")
    actions = ["approve", "reject"]

    def short(self, obj):
        return (obj.comment or "")[:40]

    @admin.action(description="Seçili yorumları onayla")
    def approve(self, request, queryset):
        queryset.update(status=CommentStatus.APPROVED, reason="admin onayı")

    @admin.action(description="Seçili yorumları reddet")
    def reject(self, request, queryset):
        queryset.update(status=CommentStatus.REJECTED, reason="admin reddi")


# -----------------------------
# Profile
# -----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bio")


# -----------------------------
# ContactMessage
# -----------------------------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "created_at")
    search_fields = ("name", "email")


# -----------------------------
# StaticPage (varsa)
# -----------------------------
try:
    from .models import StaticPage

    @admin.register(StaticPage)
    class StaticPageAdmin(admin.ModelAdmin):
        list_display = ("id", "title", "slug", "created_at")
        search_fields = ("title", "slug")

except Exception:
    # Model projede yoksa sessizce geç
    pass
