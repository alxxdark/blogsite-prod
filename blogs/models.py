from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

# -------------------------------------------------------------------
# Category
# -------------------------------------------------------------------
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name


STATUS_CHOICES = (
    ("Draft", "Draft"),
    ("Published", "Published"),
)

# -------------------------------------------------------------------
# Blog
# -------------------------------------------------------------------
class Blog(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="blogs")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blogs")
    featured_image = models.ImageField(upload_to="uploads/%Y/%m/%d", blank=True, null=True)
    short_description = models.TextField(max_length=500, blank=True)
    blog_body = models.TextField(max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft", db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "updated_at"]),
            models.Index(fields=["is_featured", "updated_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # namespaceli kullanım
        return reverse("blogs:blogs", kwargs={"slug": self.slug})

    @property
    def description(self):
        return self.blog_body

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:50] or "yazi"
            slug = base
            i = 1
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)


# -------------------------------------------------------------------
# Yorum Moderasyon Statüsü
# -------------------------------------------------------------------
class CommentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


# -------------------------------------------------------------------
# Comment  (ML alanları + indeksler)
# -------------------------------------------------------------------
class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_comments"
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    comment = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="comment_likes", blank=True)
    image = models.ImageField(upload_to="comment_images/%Y/%m/%d", blank=True, null=True)

    # ---- ML / Moderasyon ----
    status = models.CharField(max_length=10, choices=CommentStatus.choices, default=CommentStatus.PENDING)
    toxicity = models.FloatField(default=0)   # 0..1
    sentiment = models.FloatField(default=0)  # -1..1
    is_spam = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["blog", "status", "-created_at"]),
        ]

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return (self.comment or "")[:40]

    @property
    def is_visible(self):
        return self.status == CommentStatus.APPROVED


# -------------------------------------------------------------------
# Profile
# -------------------------------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)

    def __str__(self):
        return f"{getattr(self.user, 'username', 'user')} Profile"


# -------------------------------------------------------------------
# ContactMessage
# -------------------------------------------------------------------
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"


# -------------------------------------------------------------------
# StaticPage
# -------------------------------------------------------------------
class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


# -------------------------------------------------------------------
# SavedPost
# -------------------------------------------------------------------
class SavedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_posts")
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{getattr(self.user, 'username', 'user')} saved {self.post.title}"


