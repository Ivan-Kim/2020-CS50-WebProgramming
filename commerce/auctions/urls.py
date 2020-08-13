from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path("admin", admin.site.urls),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categoryitems, name="categoryitems"),
    path("<str:item>", views.item, name="item"),
    path("<str:item>/watch", views.watch, name="watch"),
    path("<str:item>/close", views.close, name="close"),
]
