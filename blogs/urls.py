from django.urls import path
from . import views

urlpatterns = [
    # Detay sayfası — home.html ile uyumlu (name='blogs')
    path("<slug:slug>/", views.blogs, name="blogs"),

    # Liste/Kategori
    path("category/<int:category_id>/", views.posts_by_category, name="posts_by_category"),

    # Aksiyonlar
    path("comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    path("<slug:slug>/like/", views.like_post, name="like_post"),
    path("<slug:slug>/save/", views.toggle_save_post, name="toggle_save_post"),

    # Profil
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),

    # Diğerleri
    path("search/", views.search, name="search"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("page/<slug:slug>/", views.static_page, name="static_page"),
]
