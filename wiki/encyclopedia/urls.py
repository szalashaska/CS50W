from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("wiki/<str:entry_name>", views.entry, name="entry"),
    path("create", views.create, name="create"),
    path("edit", views.edit, name="edit"),
    path("random", views.random, name="random"),
    path("delete", views.delete, name="delete")
]