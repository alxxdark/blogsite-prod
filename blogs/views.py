from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User

from blogs.models import Blog, Category, Comment
from blogs.forms import CommentForm

from .forms import ContactForm
from .models import ContactMessage
from .models import StaticPage


def posts_by_category(request, category_id):
    posts = Blog.objects.filter(status="Published", category=category_id)
    category = get_object_or_404(Category, pk=category_id)
    context = {"posts": posts, "category": category}
    return render(request, "posts_by_category.html", context)


def blogs(request, slug):
    """
    Tekil blog sayfası:
      - Görüntüleme sayacı +1
      - Yorumları listele (en yeni üstte)
      - POST: Yorum ekle + parent_comment ile 'yanıt' oluştur
    """
    single_blog = get_object_or_404(Blog, slug=slug, status="Published")

    # View counter
    single_blog.view_count += 1
    single_blog.save(update_fields=["view_count"])

    # Yorumlar
    comments = Comment.objects.filter(blog=single_blog).order_by('-created_at')
    comment_count = comments.count()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = single_blog
            comment.user = request.user

            # ---- Yanıt (reply) desteği ----
            parent_id = request.POST.get("parent_id")
            if parent_id:
                try:
                    parent_obj = Comment.objects.get(pk=parent_id, blog=single_blog)
                    comment.parent_comment = parent_obj
                except Comment.DoesNotExist:
                    pass  # parent bulunamazsa normal yorum olur

            comment.save()
            return HttpResponseRedirect(reverse('blogs', args=[slug]) + f'#comment_{comment.id}')
    else:
        form = CommentForm()

    context = {
        "single_blog": single_blog,
        "comments": comments,
        "comment_count": comment_count,
        "form": form,
    }
    return render(request, "blogs.html", context)


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect(f'{request.META.get("HTTP_REFERER", "/")}#comment_{comment.id}')


def search(request):
    keyword = (request.GET.get("keyword") or "").strip()
    blogs = Blog.objects.filter(status="Published")
    if keyword:
        blogs = blogs.filter(
            Q(title__icontains=keyword) |
            Q(short_description__icontains=keyword) |
            Q(blog_body__icontains=keyword)
        )
    context = {"blogs": blogs, "keyword": keyword}
    return render(request, "search.html", context)


def about(request):
    return render(request, 'about.html')


def like_post(request, slug):
    if request.user.is_authenticated:
        post = get_object_or_404(Blog, slug=slug)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        return redirect('login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    liked_posts = Blog.objects.filter(likes=profile_user)
    comments = Comment.objects.filter(user=profile_user)
    total_likes = liked_posts.count()
    total_comments = comments.count()

    context = {
        'profile_user': profile_user,
        'liked_posts': liked_posts,
        'comments': comments,
        'total_likes': total_likes,
        'total_comments': total_comments,
    }
    return render(request, 'profile.html', context)


# ---- Contact: tek sürüm (veritabanına kaydeden) ----
def contact_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            ContactMessage.objects.create(name=name, email=email, message=message)
            return render(request, 'contact_success.html')
    return render(request, 'contact.html', {'form': form})


def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, 'static_page.html', {'page': page})
