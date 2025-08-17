from django.urls import path
from . import views

urlpatterns = [
    path("<int:category_id>/", views.posts_by_category, name="posts_by_category"),

    # Blog detay
    path('blog/<slug:slug>/', views.blogs, name='blogs'),

    # Beğeni (POST + AJAX)
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('like/<slug:slug>/', views.like_post, name='like_post'),

    # KAYDET / KALDIR
    path('blog/<slug:slug>/save/', views.toggle_save_post, name='toggle_save_post'),

    # Diğerleri
    path('about/', views.about, name='about'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('contact/', views.contact_view, name='contact'),

    # En sonda statik sayfa
    path('<slug:slug>/', views.static_page, name='static_page'),

    path('profile/edit/', views.profile_edit, name='profile_edit'),
]
