from django.shortcuts import redirect, render
from django.contrib.auth import login
from blogs.models import Blog  # Category importu kullanılmıyordu
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings

# ---- Health endpoints ----
def healthz(request):
    return HttpResponse("ok", content_type="text/plain", status=200)

def home_smoke(request):
    return HttpResponse("home ok", content_type="text/plain", status=200)

# ---- Home ----
def home(request):
    # Her istek başına loaddata üretim ortamında tehlikelidir ve yavaştır;
    # ayrıca dosya bulunamazsa 500 atabilir. Bu yüzden kaldırdım.
    featured_posts = Blog.objects.filter(is_featured=True, status="Published").order_by("-updated_at")
    recent_posts_list = Blog.objects.filter(is_featured=False, status="Published").order_by("-updated_at")

    paginator = Paginator(recent_posts_list, 5)  # 5'erli sayfa
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "featured_posts": featured_posts,
        "page_obj": page_obj,
    }
    return render(request, "home.html", context)

# ---- Auth ----
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()       # kullanıcı oluştur
            login(request, user)     # otomatik giriş yaptır
            return redirect("home")  # anasayfaya yönlendir
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    context = {"form": form}
    return render(request, "register.html", context)

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")
    form = AuthenticationForm()
    context = {"form": form}
    return render(request, "login.html", context)

def logout(request):
    auth.logout(request)
    return redirect("home")

# ---- Geçici superuser endpoint (PROD'DA KAPAT) ----
def create_superuser_view(request):
    # Güvenlik: sadece DEBUG modunda ve yalnızca GET/POST'ta çalışsın.
    if not settings.DEBUG:
        return HttpResponse("Disabled on production.", status=403)

    username = "admin"
    email = "sagnak.1903@outlook.com"
    password = "Admin.Strong.Pass.129946"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        return HttpResponse("✅ Süperuser oluşturuldu.")
    return HttpResponse("ℹ️ Zaten var.")
