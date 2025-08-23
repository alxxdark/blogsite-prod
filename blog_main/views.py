from django.shortcuts import redirect, render
from assignments.models import About
from blogs.models import Blog, Category
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.core.paginator import Paginator
from django.core.management import call_command


def home(request):
    try:
        call_command("loaddata", "data.json")
    except:
        pass
    featured_posts = Blog.objects.filter(is_featured=True, status="Published").order_by("-updated_at")
    recent_posts_list = Blog.objects.filter(is_featured=False, status="Published").order_by("-updated_at")
    
    paginator = Paginator(recent_posts_list, 5)  # 5'erli sayfa
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "featured_posts": featured_posts,
        "page_obj": page_obj,
    }
    return render(request, "home.html", context)

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("register")
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
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
    context = {
        "form": form,
    }
    return render(request, "login.html", context)

def logout(request):
    auth.logout(request)
    return redirect("home")

from django.http import HttpResponse
from django.contrib.auth.models import User

def create_superuser_view(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("xxxdarkhite", "sagnak.1903@outlook.com", "Ali.129946")
        return HttpResponse("✅ Süperuser oluşturuldu.")
    return HttpResponse("ℹ️ Zaten var.")

def healthz(request):
    return HttpResponse("ok", content_type="text/plain")