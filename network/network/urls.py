
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    #API routes
    path("posts", views.create_post, name="create_post"),
    path("posts/<str:view>", views.posts, name="posts"),
    path("user/<str:user_name>", views.user_data, name="user_data"),
    path("post/<int:id>", views.edit_post, name="edit_posts")
]
