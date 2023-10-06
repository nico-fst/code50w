
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profile/<int:profile_id>", views.profile, name="profile"),
    path("toggle_follow/<int:profile_id>", views.toggle_follow, name="toggle_follow"),
    path("following", views.following, name="following"),
    path("posts/<int:post_id>", views.post, name="post"),
    path("likes", views.likes, name="likes"),
    path("toggle_like/<int:post_id>", views.toggle_like, name="toggle_like"),
]
