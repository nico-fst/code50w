from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:name>", views.entry, name='entry'),
    path("search", views.search, name='search'),
    path("create", views.create, name='create'),
    path("edit/<str:name>", views.edit, name='edit'),
    path("random_entry", views.random_entry, name='random_entry')
]
