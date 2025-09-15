from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from . import views
from django.contrib.sitemaps.views import sitemap
from blogs.sitemaps import BlogSitemap

sitemaps = {"blogs": BlogSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health
    path("healthz", views.healthz, name="healthz"),
    path("_home_smoke", views.home_smoke, name="home_smoke"),

    # Ana sayfa
    path("", views.home, name="home"),

    # Sitemap
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

    # Auth
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),   # <— login_view
    path("logout/", views.logout, name="logout"),

    # Dashboard
    path("dashboard/", include("dashboards.urls")),

    # Password reset flow
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # robots.txt
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("search/", RedirectView.as_view(pattern_name="blogs:search"), name="search"),

    # Blog app (namespace = blogs)
    path("", include(("blogs.urls", "blogs"), namespace="blogs")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if getattr(settings, "STATICFILES_DIRS", None):
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    elif getattr(settings, "STATIC_ROOT", None):
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# create_superuser route’u PROD güvenliği için kaldırıldı
# handler’lar aynı
handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
