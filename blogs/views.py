# blogs/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, F, Prefetch
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.timesince import timesince
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator  # <-- EKLENDİ

from django.conf import settings
import os

# Modeller ve formlar
from .models import (
    Profile, Blog, Category, Comment, ContactMessage, StaticPage, SavedPost, CommentStatus
)
from .forms import ProfileForm
from .forms import CommentForm  # yorum formu


# ---- Yorum görseli için basit validasyon sabitleri ----
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def _comment_json(c, parent_id=None):
    """AJAX cevap gövdesi (tek yerde toplu)."""
    return {
        "ok": True,
        "id": c.id,
        "user": getattr(c.user, "username", str(c.user)),
        "comment": c.comment,
        "created": f"{timesince(c.created_at)} ago",
        "parent_id": parent_id,
        "like_count": c.likes.count(),
        "status": c.status,
        "reason": c.reason,
        "image_url": (c.image.url if getattr(c, "image", None) else None),
    }


# -----------------------
# LİSTELEME / KATEGORİ
# -----------------------
def posts_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    posts = Blog.objects.filter(status="Published", category=category).order_by("-updated_at")
    return render(request, "posts_by_category.html", {"posts": posts, "category": category})


# -----------------------
# DETAY SAYFASI (blogs.html)
# -----------------------
def blogs(request, slug):
    """
    Tekil blog + yorum yazma formu ÜSTTE + altta sayfalı kök yorumlar (+cevaplar).
    """
    single_blog = get_object_or_404(Blog, slug=slug, status="Published")

    # View counter
    Blog.objects.filter(pk=single_blog.pk).update(view_count=F("view_count") + 1)
    single_blog.refresh_from_db(fields=["view_count"])

    # Onaylı kök yorumlar (+1 seviye onaylı cevapları prefetch)
    replies_qs = Comment.objects.filter(status=CommentStatus.APPROVED).select_related("user").order_by("created_at")
    roots_qs = (
        Comment.objects.filter(
            blog=single_blog,
            status=CommentStatus.APPROVED,
            parent_comment__isnull=True,
        )
        .select_related("user")
        .prefetch_related(Prefetch("replies", queryset=replies_qs))
        .order_by("-created_at")
    )
    comment_count = roots_qs.count()

    # Yorum gönderimi (aynı sayfaya POST)
    if request.method == "POST":
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if not request.user.is_authenticated:
            if is_ajax:
                return JsonResponse({"ok": False, "error": "auth_required"}, status=403)
            return redirect("login")

        text = (request.POST.get("comment") or "").strip()
        if not text:
            if is_ajax:
                return JsonResponse({"ok": False, "error": "empty"}, status=400)
            return HttpResponseRedirect(reverse("blogs:blogs", args=[slug]) + "#comments")

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

        # (İsteğe bağlı) Görsel
        img = request.FILES.get("image")
        if img:
            if img.content_type not in ALLOWED_IMAGE_TYPES:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "bad_image_type"}, status=400)
                messages.error(request, "Desteklenmeyen görsel türü.")
                return HttpResponseRedirect(reverse("blogs:blogs", args=[slug]) + "#comments")
            if img.size > MAX_IMAGE_SIZE:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": "too_large"}, status=400)
                messages.error(request, "Görsel en fazla 5 MB olmalı.")
                return HttpResponseRedirect(reverse("blogs:blogs", args=[slug]) + "#comments")
            comment.image = img  # models.py'de Comment.image alanı olmalı

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
            return JsonResponse(_comment_json(comment, parent_id=parent_id or None))

        # Normal redirect (yorumlara dön)
        return HttpResponseRedirect(reverse("blogs:blogs", args=[slug]) + "#comments")

    # ---- KÖK yorumlarda sayfalama ----
    cpage = request.GET.get("cpage", 1)
    paginator = Paginator(roots_qs, 10)  # her sayfada 10 kök yorum
    c_page_obj = paginator.get_page(cpage)
    comments = c_page_obj.object_list  # sadece bu sayfanın kök yorumları

    # is_saved bayrağı
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedPost.objects.filter(user=request.user, post=single_blog).exists()

    context = {
        "single_blog": single_blog,
        "comments": comments,
        "comment_count": comment_count,
        "c_page_obj": c_page_obj,   # <-- template'te sayfalama için
        "form": CommentForm(),
        "is_saved": is_saved,
    }
    return render(request, "blogs.html", context)


# -----------------------
# LIKE / SAVE
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
    return redirect(request.META.get("HTTP_REFERER", reverse("blogs:blogs", args=[slug])))


# -----------------------
# PROFİL
# -----------------------
@login_required
def profile_edit(request, username):
    # Hangi profili düzenliyoruz?
    target_user = get_object_or_404(User, username=username)

    # Sadece sahibi (veya staff/superuser) düzenleyebilsin
    if request.user != target_user and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Bu profili düzenleme yetkin yok.")
        return redirect("blogs:profile", username=target_user.username)

    profile, _ = Profile.objects.get_or_create(user=target_user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilin güncellendi.")
            return redirect("blogs:profile", username=target_user.username)
        messages.error(request, "Formda hatalar var. Lütfen kontrol et.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile_edit.html", {"form": form, "profile_user": target_user})

@login_required
def profile_edit_me(request):
    # Kullanıcı adını otomatik ekleyip doğru route'a yönlendir
    return redirect("blogs:profile_edit", username=request.user.username)


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


# -----------------------
# Ayrı comment_add endpoint'i (kullanıyorsan)
# -----------------------
@require_POST
def comment_add(request, post_id):
    post = get_object_or_404(Blog, id=post_id, status="Published")
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({"ok": False, "error": "auth_required"}, status=403)
        return redirect("login")

    text = (request.POST.get("comment") or "").strip()
    if not text:
        if is_ajax:
            return JsonResponse({"ok": False, "error": "empty"}, status=400)
        return redirect("blogs:blogs", slug=post.slug)

    c = Comment(blog=post, user=request.user, comment=text, created_at=timezone.now())

    parent_id = request.POST.get("parent_id")
    if parent_id:
        try:
            c.parent_comment = Comment.objects.get(pk=parent_id, blog=post)
        except Comment.DoesNotExist:
            pass

    # (İsteğe bağlı) Görsel
    img = request.FILES.get("image")
    if img:
        if img.content_type not in ALLOWED_IMAGE_TYPES:
            if is_ajax:
                return JsonResponse({"ok": False, "error": "bad_image_type"}, status=400)
            messages.error(request, "Desteklenmeyen görsel türü.")
            return redirect("blogs:blogs", slug=post.slug)
        if img.size > MAX_IMAGE_SIZE:
            if is_ajax:
                return JsonResponse({"ok": False, "error": "too_large"}, status=400)
            messages.error(request, "Görsel en fazla 5 MB olmalı.")
            return redirect("blogs:blogs", slug=post.slug)
        c.image = img

    c.save()

    if c.status == CommentStatus.APPROVED:
        messages.success(request, "Yorumun yayınlandı. 🤖")
    elif c.status == CommentStatus.PENDING:
        messages.info(request, "Yorumun moderasyon bekliyor. 🤖")
    else:
        messages.warning(request, "Yorumun kurallara uymadığı için reddedildi. 🤖")

    if is_ajax:
        return JsonResponse(_comment_json(c, parent_id=parent_id or None))

    return redirect("blogs:blogs", slug=post.slug)
