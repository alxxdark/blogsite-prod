from django.urls import path
from . import views

urlpatterns = [
    path("<int:category_id>/", views.posts_by_category, name="posts_by_category"),
    path('blog/<slug:slug>/', views.blogs, name='blogs'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),  # fallback
    path('about/', views.about, name='about'),
    path('like/<slug:slug>/', views.like_post, name='like_post'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('contact/', views.contact_view, name='contact'),
    path('<slug:slug>/', views.static_page, name='static_page'),

    # AJAX/API
    path('api/comment/<int:comment_id>/like/', views.like_comment_api, name='like_comment_api'),
    path('api/blog/<slug:slug>/comment/', views.add_comment_api, name='add_comment_api'),
]
