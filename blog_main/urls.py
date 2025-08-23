"""
URL configuration for blog_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from blogs import views as BlogsView
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .views import healthz


urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.home, name="home"),
    path("category/",include("blogs.urls")),
    path("blogs/<slug:slug>/", BlogsView.blogs,name="blogs"),
    path("blogs/search",BlogsView.search,name="search"),
    path("register/", views.register, name="register"),
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
    path("create-superuser/", views.create_superuser_view),
    path("healthz", healthz),  # buraya ekledik
    path("", include("blogs.urls")),  # mevcut blog app’ini bağlayan kısım

    

    #dashboards
    path("dashboard/", include("dashboards.urls")),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', include('blogs.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

@require_http_methods(["GET","HEAD"])
def healthz(_):  # hafif ping
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # ...
    path("healthz/", healthz, name="healthz"),
]