from django.contrib.sitemaps import Sitemap
from .models import Blog

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Blog.objects.filter(is_published=True).order_by("-updated_at")   

    def lastmod(self, obj: Blog):
        return getattr(obj, "updated_at", None)

    def location(self, obj: Blog):
        return obj.get_absolute_url()
