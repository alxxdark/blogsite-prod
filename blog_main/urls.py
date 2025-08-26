"""
URL configuration for blog_main project.
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Ana sayfa
    path("", views.home, name="home"),

    # Blog rotaları (blogs/urls içinden gelsin)
    path("", include("blogs.urls")),

    # Auth
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    # Geçici: superuser (prod’da kapat)
    path("create-superuser/", views.create_superuser_view),

    # Dashboard
    path("dashboard/", include("dashboards.urls")),

    # Password reset flow
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# DEBUG iken statik
if settings.DEBUG:
    if getattr(settings, "STATICFILES_DIRS", None):
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    elif getattr(settings, "STATIC_ROOT", None):
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
