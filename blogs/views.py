from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timesince import timesince
from django.utils import timezone

from blogs.models import Blog, Category, Comment, ContactMessage, StaticPage, SavedPost
from blogs.forms import CommentForm


def posts_by_category(request, category_id):
    posts = Blog.objects.filter(status="Published", category=category_id)
    category = get_object_or_404(Category, pk=category_id)
    return render(request, "posts_by_category.html", {"posts": posts, "category": category})


def blogs(request, slug):
    """
    Tekil blog + yorumlar + is_saved bayrağı.
    """
    single_blog = get_object_or_404(Blog, slug=slug, status="Published")

    # View counter
    single_blog.view_count += 1
    single_blog.save(update_fields=["view_count"])

    comments = Comment.objects.filter(blog=single_blog).order_by('-created_at')
    comment_count = comments.count()

    if request.method == "POST":
        if not request.user.is_authenticated:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "error": "auth_required"}, status=403)
            return redirect('login')

        text = (request.POST.get("comment") or "").strip()
        if not text:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "error": "empty"}, status=400)
            return HttpResponseRedirect(reverse('blogs', args=[slug]))

        comment = Comment(
            blog=single_blog,
            user=request.user,
            comment=text,
            created_at=timezone.now()
        )
        parent_id = request.POST.get("parent_id")
        if parent_id:
            try:
                parent_obj = Comment.objects.get(pk=parent_id, blog=single_blog)
                comment.parent_comment = parent_obj
            except Comment.DoesNotExist:
                pass
        comment.save()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "ok": True,
                "id": comment.id,
                "user": request.user.username,
                "comment": comment.comment,
                "created": f"{timesince(comment.created_at)} ago",
                "parent_id": parent_id or None,
                "like_count": comment.likes.count(),
            })

        return HttpResponseRedirect(reverse('blogs', args=[slug]) + f'#comment_{comment.id}')

    # is_saved bilgisi (butonun durumu için)
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


@require_POST
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


@require_POST
@login_required
def like_post(request, slug):
    post = get_object_or_404(Blog, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "likes": post.likes.count()})

    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ---- YENİ: Kaydet / Kaldır ----
@require_POST
@login_required
def toggle_save_post(request, slug):
    post = get_object_or_404(Blog, slug=slug, status="Published")
    obj, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if created:
        saved = True
    else:
        obj.delete()
        saved = False

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "saved": saved})

    # normal fallback
    return redirect(request.META.get('HTTP_REFERER', reverse('blogs', args=[slug])))


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    liked_posts = Blog.objects.filter(likes=profile_user)
    comments = Comment.objects.filter(user=profile_user)
    total_likes = liked_posts.count()
    total_comments = comments.count()

    # YENİ: kaydedilenler
    saved_posts = SavedPost.objects.filter(user=profile_user).select_related("post")

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'liked_posts': liked_posts,
        'comments': comments,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'saved_posts': saved_posts,
    })


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
    return render(request, 'about.html')


def contact_view(request):
    from blogs.forms import ContactForm
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            return render(request, 'contact_success.html')
    return render(request, 'contact.html', {'form': form})


def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, 'static_page.html', {'page': page})
