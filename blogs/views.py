from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from blogs.models import Blog, Category, Comment
from blogs.forms import CommentForm
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import ContactForm
from .models import ContactMessage
from .models import StaticPage
def posts_by_category(request, category_id):
    posts = Blog.objects.filter(status="Published", category=category_id)
    category = get_object_or_404(Category, pk=category_id)
    context = {"posts": posts, "category": category}
    return render(request, "posts_by_category.html", context)

def blogs(request, slug):
    single_blog = get_object_or_404(Blog, slug=slug, status="Published")
    single_blog.view_count += 1
    single_blog.save()

    comments = Comment.objects.filter(blog=single_blog).order_by('-created_at')
    comment_count = comments.count()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = single_blog
            comment.user = request.user
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
    keyword = request.GET.get("keyword")
    blogs = Blog.objects.filter(Q(title__icontains=keyword) | Q(short_description__icontains=keyword) | Q(blog_body__icontains=keyword), status="Published")
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


def contact_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Şimdilik sadece başarı şablonuna yönlendirelim
            return render(request, 'contact_success.html')
    return render(request, 'contact.html', {'form': form})


def contact_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Veritabanına kaydet
            ContactMessage.objects.create(name=name, email=email, message=message)
            return render(request, 'contact_success.html')
    return render(request, 'contact.html', {'form': form})


def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, 'static_page.html', {'page': page})