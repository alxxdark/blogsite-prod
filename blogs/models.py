from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse




class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural="categories"

    def __str__(self):
        return self.category_name
    
STATUS_CHOCİES= (
     ("Draft","Draft"),
     ("Published","Published")
)    
    
class Blog(models.Model):
        title = models.CharField(max_length=100)
        slug = models.SlugField(max_length=100, unique=True, blank=True)
        category = models.ForeignKey(Category, on_delete=models.CASCADE)
        author = models.ForeignKey(User, on_delete=models.CASCADE)
        featured_image = models.ImageField(upload_to="uploads/%Y/%m/%d")
        short_description = models.TextField(max_length=500)
        blog_body =  models.TextField(max_length=2000)  
        status = models.CharField(max_length=20, choices=STATUS_CHOCİES, default="Draft")
        is_featured = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
        # Görüntülenme
        view_count = models.IntegerField(default=0)

        def __str__(self):
             return self.title
        def get_absolute_url(self):
        # senin urls.py’de detay adı 'blogs'
            return reverse('blogs', kwargs={'slug': self.slug})

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    def total_likes(self):
        return self.likes.count()
    def __str__(self):
          return self.comment
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title