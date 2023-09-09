from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
    pass  # inherits from AbstractUser: nur für zusätzliche Felder zusätzliche Deklarationen nötig


class Listing(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=256)
    price = models.FloatField()
    url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    opened = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='owned_listings')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='won_listings')

    def __str__(self):
        return f"{self.title} ({self.id}) @{self.owner}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField()

    def __str__(self):
        return f"{self.user}: {self.amount} on {self.listing}"
    

class Comment(models.Model):
    content = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.user} commented on {self.listing} ({self.time})"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user}: {self.listing}"