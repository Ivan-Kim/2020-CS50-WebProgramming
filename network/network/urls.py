from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("admin", admin.site.urls),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:username>", views.profile, name="profile"),
    path("edit/<int:postid>", views.edit, name="edit"),
    path("like/<int:postid>", views.like, name="like"),
    path("follow/<str:name>", views.follow, name="follow"),
    path("followings/like/<int:postid>", views.like, name="followingslike"),
    path("followings/<str:name>", views.followings, name="followings"),
]
