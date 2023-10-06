from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Like


def index(request):
    all_posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "page": page,
        "likes": None if request.user.is_anonymous else Like.objects.filter(user=request.user).values_list('post__id', flat=True)
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    


class NewPostForm(forms.Form):
    content = forms.CharField(label=False, max_length=256, widget=forms.Textarea(attrs={'placeholder': 'Share your opinion...'}))

def new_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = Post(user=request.user, content=form.cleaned_data['content'])
            post.save()
            return HttpResponseRedirect(reverse("index"))
        #TODO else:
    return render(request, "network/new_post.html", {
            "form": NewPostForm()
        })


def profile(request, profile_id):
    user = User.objects.get(id=profile_id)
    return render(request, "network/profile.html", {
        "profile": user,
        "followers": user.followers.count(),
        "following": user.following.count(),
        "posts": Post.objects.filter(user=user).order_by("-timestamp"),
        "button_text": "Unfollow" if request.user.is_authenticated and request.user != user and request.user.following.filter(id=user.id).exists() else "Follow"
    })


def toggle_follow(request, profile_id):
    if request.user.is_authenticated:
        profile = User.objects.get(id=profile_id)
        if profile in request.user.following.all():
            request.user.following.remove(profile)
        else:
            request.user.following.add(profile)
        return redirect('profile', profile_id=profile_id)
    

def following(request):
    following_users = request.user.following.all()
    following_posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')
    
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "page": page,
    })


@csrf_exempt
@login_required
def post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if request.method == "GET":
            return JsonResponse(post.serialize())
        elif request.method == "PUT":
            data = json.loads(request.body)
            if data.get("content") is not None:
                post.content = data["content"]
                post.save()
            if data.get("like") is not None:
                like = Like(user=request.user, post=post)
                like.save()
            return HttpResponse(status=204)
    except Post.DoesNotExist :
        return HttpResponse(status=404)
    except Exception as e:
        return HttpResponse(status=500)
    

@csrf_exempt
@login_required
def likes(request):
    try:
        likes = Like.objects.filter(user=request.user)
        serialized_likes = [like.serialize() for like in likes]
        return JsonResponse(serialized_likes, safe=False)
    except Like.DoesNotExist:
        return HttpResponse(status=404)
    except Exception as e:
        return HttpResponse(status=500)


@csrf_exempt
@login_required
def toggle_like(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if created:  # falls bei _or_created erstellt
        return JsonResponse({'message': 'like added'})
 
    like.delete()  # sonst löschen
    return JsonResponse({'message': 'like removed'})
