from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings

from blogs.models import Blog
from .forms import RegistrationForm


# ---- Health endpoints ----
def healthz(request):
    return HttpResponse("ok", content_type="text/plain", status=200)

def home_smoke(request):
    return HttpResponse("home ok", content_type="text/plain", status=200)


# ---- Home ----
def home(request):
    featured_posts = Blog.objects.filter(
        is_featured=True, status="Published"
    ).order_by("-updated_at")

    recent_posts_qs = Blog.objects.filter(
        is_featured=False, status="Published"
    ).order_by("-updated_at")

    page_obj = Paginator(recent_posts_qs, 5).get_page(request.GET.get("page"))

    return render(request, "home.html", {
        "featured_posts": featured_posts,
        "page_obj": page_obj,
    })


# ---- Auth ----
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()             # User oluştur
            auth_login(request, user)      # Otomatik giriş
            messages.success(request, "Aramıza hoş geldin! 🎉")
            return redirect("home")        # Anasayfaya yönlendir
        messages.error(request, "Formda hatalar var. Lütfen kontrol et.")
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, f"Tekrar hoş geldin, {user.username}!")
            nxt = request.GET.get("next") or request.POST.get("next")
            return redirect(nxt or "home")
        messages.error(request, "Kullanıcı adı veya şifre hatalı.")
    else:
        form = AuthenticationForm(request)
    return render(request, "login.html", {"form": form})


def logout(request):
    auth.logout(request)
    messages.info(request, "Çıkış yapıldı.")
    return redirect("home")
