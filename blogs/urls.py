from django.urls import path
from . import views

urlpatterns = [
    # --- Önce spesifik yollar ---
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),

    # Blog detay ve aksiyonlar
    path('blog/<slug:slug>/save/', views.toggle_save_post, name='toggle_save_post'),
    path('blog/<slug:slug>/', views.blogs, name='blogs'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('like/<slug:slug>/', views.like_post, name='like_post'),

    # Diğer sayfalar
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # Kategori (istersen bunu 'category/<int:category_id>/' yapman çakışmaları iyice engeller)
    path('<int:category_id>/', views.posts_by_category, name='posts_by_category'),

    # --- EN SON: catch-all statik sayfa ---
    path('<slug:slug>/', views.static_page, name='static_page'),
]
