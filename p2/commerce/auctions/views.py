from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Category, Bid, Watchlist, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(opened=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class NewListingForm(forms.Form):
    title = forms.CharField(label=False, max_length=32, widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    description = forms.CharField(label=False, max_length=256, widget=forms.Textarea(attrs={'placeholder': 'Tell us about your new listing...'}))
    starting_bid = forms.FloatField(label=False, widget=forms.NumberInput(attrs={'placeholder': 'Starting Bid'}))
    url = forms.URLField(label=False, required=False,widget=forms.TextInput(attrs={'placeholder': '(Opt: Provide URL of your Photo)'}))
    CHOICES = [(category.id, category.name) for category in Category.objects.all()]
    category = forms.ChoiceField(label=False, choices=CHOICES, widget=forms.Select(attrs={'class': 'custom-select'}))


def new_listing(request):
    if request.method == 'POST':
        form = NewListingForm(request.POST)
        if form.is_valid():            
            listing = Listing(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                price=form.cleaned_data["starting_bid"],
                url=form.cleaned_data["url"],
                category=Category.objects.get(id=form.cleaned_data["category"]),
                owner=request.user
            )
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=[listing.id]))
        else:
            render(request, "auctions/new_listing.html", {
                "form": NewListingForm(),
                "message": "Input not valid!"  #! erscheint bisher nicht
            })
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })


class NewBidForm(forms.Form):
    bid = forms.FloatField(label=False, widget=forms.NumberInput())


class NewCommentForm(forms.Form):
    content = forms.CharField(label=False, max_length=256, widget=forms.Textarea(attrs={'placeholder': 'Your thoughts...'}))


def listing(request, id, message=None):
    listing = Listing.objects.get(id=id)
    onWatchlist = Watchlist.objects.filter(user=request.user.id, listing=id)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "form": NewBidForm(initial={'bid': listing.price}),
        "onWatchlist": onWatchlist,
        "message": message,
        "closable": request.user == listing.owner and listing.opened,
        "won": request.user == listing.winner and not listing.opened,
        "comments": Comment.objects.filter(listing=id),
        "comment_form": NewCommentForm()
    })


def watchlist(request, message=None, alert=None):
    if request.method == "GET":
        return render(request, "auctions/watchlist.html", {
            "watchlist": Watchlist.objects.filter(user=request.user.id),
            "message": message,
            "alert": alert
        })
    return HttpResponse("Here is nothing to look at...")


def watchlist_add(request, id):
    listing = get_object_or_404(Listing, id=id)
    w = Watchlist(user=request.user, listing=listing)
    w.save()
    return redirect('watchlist', message=f"{listing.title} added to watchlist")


def watchlist_remove(request, id):
    try:
        w = Watchlist.objects.get(user=request.user, listing=id)
        w.delete()
        return redirect('watchlist', message=f"{w.listing.title} removed from watchlist")
    except ObjectDoesNotExist:
        return watchlist(request, None, "Error while trying to remove")


def bid(request, listing):
    if request.method == 'POST':
        form = NewBidForm(request.POST)
        if form.is_valid():
            l = Listing.objects.get(id=listing)
            b = Bid(user=request.user, listing=l, amount=form.cleaned_data['bid'])
            b.save()

            # vor speichern prüfen, ob bisher höchstes Gebot
            if b.amount > l.price:
                l.price = b.amount
                l.winner = request.user
                l.save()
                return redirect('listing', id=l.id, message=f"You bid {b.amount} on {l.title}")
            else:
                return redirect('listing',
                                id=l.id,
                                message=f"You could not bid {b.amount} on {l.title} since the current price {l.price} is already higher")

    else:
        return HttpResponse("Here is nothing to look at...")


def categories(request, filter):
    category = None  # Name of filter
    if filter:
        category = Category.objects.get(id=filter)
        listings_filtered = Listing.objects.filter(category=category)
    else:
        listings_filtered = Listing.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
        "listings": listings_filtered,
        "filter": filter,
        "category": category
    })


def my_listings(request):
    return render(request, "auctions/my_listings.html", {
        "open_listings": Listing.objects.filter(owner=request.user.id, opened=True),
        "closed_listings": Listing.objects.filter(owner=request.user.id, opened=False),
        "won_listings": Listing.objects.filter(winner=request.user.id, opened=False)
    })


def close_listing(request, listing):
    l = Listing.objects.get(id=listing)
    if request.user == l.owner:
        l.opened = False
        l.save()
        return HttpResponseRedirect(reverse("my_listings"))
    else:
        return render(request, "auctions/index.html", {
            "message": "You are not allowed to close this listing"
        })
    

def comment(request, id):
    if request.method == "POST":
        if request.user is not None:
            form = NewCommentForm(request.POST)
            if form.is_valid():
                c = Comment(
                    content=form.cleaned_data['content'],
                    user=request.user,
                    listing=Listing.objects.get(id=id),
                )
                c.save()
                return HttpResponseRedirect(reverse("listing", args=[id]))
        return HttpResponse("You have to be logged in to comment")