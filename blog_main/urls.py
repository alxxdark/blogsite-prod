"""
URL configuration for blog_main project.
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from . import views
from blogs import views as BlogsView
from django.contrib.auth import views as auth_views
from .health import healthz  # healthz artık ayrı dosyada, app'lere dokunmaz

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ana sayfa
    path("", views.home, name="home"),

    # Blog ile ilgili rotalar (senin kullandıkların aynen kalsın)
    path("category/", include("blogs.urls")),
    path("blogs/<slug:slug>/", BlogsView.blogs, name="blogs"),
    path("blogs/search", BlogsView.search, name="search"),

    # Auth
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    # Geçici: superuser oluşturma (prod'da kapatmayı unutma)
    path("create-superuser/", views.create_superuser_view),

    # Healthcheck
    path("healthz", healthz),

    # Dashboards
    path("dashboard/", include("dashboards.urls")),

    # Password reset flow
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # blogs urls (sen daha önce eklemiştin—tek kopya yeterli)
    path('', include('blogs.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# DEBUG iken statik dosyalar (senin mevcut düzenine dokunmadım)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
