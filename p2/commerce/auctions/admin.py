from django.contrib import admin
from .models import Listing, Category, User, Bid, Watchlist, Comment

# Register your models here.
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Watchlist)
admin.site.register(Comment)