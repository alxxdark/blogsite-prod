from django.urls import path
from . import views

urlpatterns = [
    # Liste/Kategori/aksiyonlar/profil/diğerleri önce
    path("category/<int:category_id>/", views.posts_by_category, name="posts_by_category"),
    path("comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    path("<slug:slug>/like/", views.like_post, name="like_post"),
    path("<slug:slug>/save/", views.toggle_save_post, name="toggle_save_post"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("search/", views.search, name="search"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("page/<slug:slug>/", views.static_page, name="static_page"),

    # >>> EN SON: tek segmentli slug detayı <<<
    path("<slug:slug>/", views.blogs, name="blogs"),
]
