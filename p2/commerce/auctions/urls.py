from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("listing/<int:id>/<str:message>", views.listing, name="listing"),
    path("watchlist/<str:message>", views.watchlist, name="watchlist"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("bid/<str:listing>", views.bid, name="bid"),
    path("categories/<str:filter>", views.categories, name="categories"),
    path("categories/", views.categories, kwargs={'filter': None}, name="categories"),
    path("watchlist_remove/<int:id>", views.watchlist_remove, name="watchlist_remove"),
    path("watchlist_add/<int:id>", views.watchlist_add, name="watchlist_add"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("close_listing/<str:listing>", views.close_listing, name="close_listing"),
    path("comment/<int:id>", views.comment, name="comment"),
]
