from django.shortcuts import get_object_or_404, redirect, render
from blogs.models import Blog, Category
from .forms import AddUserForm, BlogPostForm, CategoryForm, EditUserForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/')
    category_count = Category.objects.all().count()
    blogs_count = Blog.objects.all().count()
    context = {
        "category_count": category_count,
        "blogs_count": blogs_count,
    }
    return render(request, "dashboard/dashboard.html", context)

def categories(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    return render(request, "dashboard/categories.html", context)

def add_category(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("categories")
    else:
        form = CategoryForm()
    context = {"form": form}
    return render(request, "dashboard/add_category.html", context)

def edit_category(request, pk):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("categories")
    else:
        form = CategoryForm(instance=category)
    context = {"form": form, "category": category}
    return render(request, "dashboard/edit_category.html", context)

def delete_category(request, pk):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect("categories")

def posts(request):
    if not request.user.is_authenticated:
        return redirect('/')
    # Admin tarafı: tüm yazıları listelemek mantıklı, en yeniler en üstte
    post_list = Blog.objects.all().order_by('-id')
    paginator = Paginator(post_list, 5)  # sayfa başı 5 post
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, "dashboard/posts.html", context)

def add_post(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # ÖNEMLİ: Sadece 1 kez save; slug'ı model otomatik oluşturacak
            post.save()
            return redirect("posts")
    else:
        form = BlogPostForm()
    context = {"form": form}
    return render(request, "dashboard/add_post.html", context)

def edit_post(request, pk):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    post = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            # Slug'ı elle değiştirmiyoruz; mevcut slug sabit kalır (SEO için iyi)
            form.save()
            return redirect("posts")
    else:
        form = BlogPostForm(instance=post)
    context = {"form": form, "post": post}
    return render(request, "dashboard/edit_post.html", context)

def delete_post(request, pk):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    post = get_object_or_404(Blog, pk=pk)
    post.delete()
    return redirect("posts")

def users(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    users = User.objects.all()
    context = {"users": users}
    return render(request, "dashboard/users.html", context)

def add_user(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    if request.method == "POST":
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users")
    else:
        form = AddUserForm()
    context = {"form": form}
    return render(request, "dashboard/add_user.html", context)

def edit_user(request, pk):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("users")
    else:
        form = EditUserForm(instance=user)
    context = {"form": form}
    return render(request, "dashboard/edit_user.html", context)

def delete_user(request, pk):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect("users")
