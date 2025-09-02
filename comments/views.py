from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from blogs.models import Blog
from .forms import CommentForm

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Blog, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST, request=request)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.user = request.user
            comment.save()
    return redirect(post.get_absolute_url())
