from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.timesince import timesince

from django.conf import settings
import os

# Modeller ve formlar
from .models import (
    Profile, Blog, Category, Comment, ContactMessage, StaticPage, SavedPost, CommentStatus
)
from .forms import ProfileForm
from .forms import CommentForm  # yorum formu

# -----------------------
# LİSTELEME / KATEGORİ
# -----------------------
def posts_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    posts = Blog.objects.filter(status="Published", category=category).order_by("-updated_at")
    return render(request, "posts_by_category.html", {"posts": posts, "category": category})

# -----------------------
# DETAY SAYFASI (blogs.html)
# URL name='blogs' -> home.html ile uyumlu
# -----------------------
def blogs(request, slug):
    """
    Tekil blog + yorumlar + like + kaydetme butonu.
    """
    single_blog = get_object_or_404(Blog, slug=slug, status="Published")

    # View counter (yarış koşullarında güvenli)
    Blog.objects.filter(pk=single_blog.pk).update(view_count=F("view_count") + 1)
    single_blog.refresh_from_db(fields=["view_count"])

    # SADECE ONAYLI KÖK YORUMLAR (cevaplar include içinde r.is_visible ile süzülür)
    comments = Comment.objects.filter(
        blog=single_blog,
        status=CommentStatus.APPROVED,
        parent_comment__isnull=True
    ).order_by("-created_at")
    comment_count = comments.count()

    # YORUM GÖNDERİMİ (aynı sayfaya POST)
    if request.method == "POST":
        # AJAX mı?
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if not request.user.is_authenticated:
            if is_ajax:
                return JsonResponse({"ok": False, "error": "auth_required"}, status=403)
            return redirect("login")

        text = (request.POST.get("comment") or "").strip()
        if not text:
            if is_ajax:
                return JsonResponse({"ok": False, "error": "empty"}, status=400)
            return HttpResponseRedirect(reverse("blogs", args=[slug]))

        # Yeni yorum objesi
        comment = Comment(
            blog=single_blog,
            user=request.user,
            comment=text,
            created_at=timezone.now(),
        )

        # Yanıt ise parent bağla
        parent_id = request.POST.get("parent_id")
        if parent_id:
            try:
                parent_obj = Comment.objects.get(pk=parent_id, blog=single_blog)
                comment.parent_comment = parent_obj
            except Comment.DoesNotExist:
                pass

        # Kaydet -> signals.auto_moderate_comment ML çalıştırır
        comment.save()

        # Duruma göre kullanıcı mesajı
        if comment.status == CommentStatus.APPROVED:
            messages.success(request, "Yorumun yayınlandı. 🤖")
        elif comment.status == CommentStatus.PENDING:
            messages.info(request, "Yorumun moderasyon bekliyor. 🤖")
        else:
            messages.warning(request, "Yorumun kurallara uymadığı için reddedildi. 🤖")

        # AJAX cevap
        if is_ajax:
            return JsonResponse({
                "ok": True,
                "id": comment.id,
                "user": request.user.username,
                "comment": comment.comment,
                "created": f"{timesince(comment.created_at)} ago",
                "parent_id": parent_id or None,
                "like_count": comment.likes.count(),
                "status": comment.status,     # front-end istersen kullanabilir
                "reason": comment.reason,     # moderasyon nedeni
            })

        # Normal redirect (yeni yoruma anchor ile dön)
        return HttpResponseRedirect(reverse("blogs", args=[slug]) + f"#comment_{comment.id}")

    # is_saved bayrağı
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedPost.objects.filter(user=request.user, post=single_blog).exists()

    context = {
        "single_blog": single_blog,
        "comments": comments,
        "comment_count": comment_count,
        "form": CommentForm(),
        "is_saved": is_saved,
    }
    return render(request, "blogs.html", context)

# -----------------------
# LIKE / SAVE AKSİYONLARI
# -----------------------
@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "comment_id": comment.id, "like_count": comment.likes.count()})
    return redirect(f'{request.META.get("HTTP_REFERER", "/")}#comment_{comment.id}')

@login_required
def like_post(request, slug):
    post = get_object_or_404(Blog, slug=slug, status="Published")
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "likes": post.likes.count()})
    return redirect(request.META.get("HTTP_REFERER", "home"))

@login_required
def toggle_save_post(request, slug):
    post = get_object_or_404(Blog, slug=slug, status="Published")
    obj, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    saved = True if created else False
    if not created:
        obj.delete()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "saved": saved})
    return redirect(request.META.get("HTTP_REFERER", reverse("blogs", args=[slug])))

# -----------------------
# PROFİL
# -----------------------
@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilin güncellendi.")
            return redirect("profile", username=request.user.username)
        messages.error(request, "Formda hatalar var. Lütfen kontrol et.")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profile_edit.html", {"form": form})

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile_obj, _ = Profile.objects.get_or_create(user=profile_user)

    liked_posts = Blog.objects.filter(likes=profile_user)
    comments = Comment.objects.filter(user=profile_user)
    saved_posts = SavedPost.objects.filter(user=profile_user).select_related("post")

    context = {
        "profile_user": profile_user,
        "profile": profile_obj,
        "liked_posts": liked_posts,
        "comments": comments,
        "saved_posts": saved_posts,
        "total_likes": liked_posts.count(),
        "total_comments": comments.count(),
    }
    return render(request, "profile.html", context)

# -----------------------
# ARAMA / HAKKIMIZDA / İLETİŞİM / STATİK SAYFA
# -----------------------
def search(request):
    keyword = (request.GET.get("keyword") or "").strip()
    blogs = Blog.objects.filter(status="Published")
    if keyword:
        blogs = blogs.filter(
            Q(title__icontains=keyword) |
            Q(short_description__icontains=keyword) |
            Q(blog_body__icontains=keyword)
        )
    return render(request, "search.html", {"blogs": blogs, "keyword": keyword})

def about(request):
    return render(request, "about.html")

def contact_view(request):
    from .forms import ContactForm
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ContactMessage.objects.create(
            name=form.cleaned_data["name"],
            email=form.cleaned_data["email"],
            message=form.cleaned_data["message"],
        )
        return render(request, "contact_success.html")
    return render(request, "contact.html", {"form": form})

def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, "static_page.html", {"page": page})

# -----------------------
# Depolama kontrol (opsiyonel)
# -----------------------
def storage_debug(request):
    masked = bool(os.environ.get("CLOUDINARY_URL"))
    return HttpResponse(
        f"STORAGE={getattr(settings, 'DEFAULT_FILE_STORAGE', 'local')}<br>CLOUDINARY_URL set? {masked}"
    )
