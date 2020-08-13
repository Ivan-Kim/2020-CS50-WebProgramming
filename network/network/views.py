from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from django.http import JsonResponse
from django.core import serializers
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.views.generic import ListView
import json


from .models import User, Comment, Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        exclude = ('likes', 'comments')
        labels = {'body': "New Post"}
        widgets = {'op': forms.HiddenInput(), 
                    'body': forms.Textarea(),
                    'timestamp': forms.HiddenInput}

def paginate(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def index(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "networks/error.html")
    else:
        posts = list(reversed(Post.objects.all()))
        return render(request, "network/index.html", {"newpost": PostForm(initial={'op': request.user}), 'posts': paginate(request, posts)})


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

def profile(request, username):
    profileuser = User.objects.get(username=username)
    posts = list(reversed(profileuser.posts.all()))
    return render(request, "network/profile.html", {"profileuser": profileuser, "posts": paginate(request, posts)})

@csrf_exempt
def edit(request, postid):
    try:
        post = Post.objects.get(id=postid)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)
    # cannot edit unless user is original poster
    if post.op != request.user:
        return JsonResponse({
            "error": "You do not have access to edit."
        }, status=400)
    # update post content via PUT request
    if request.method == 'PUT':
        data = json.loads(request.body)
        if data.get("body")is not None:
            post.body=data["body"]
            post.save(update_fields=["body"])
            return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

@csrf_exempt
def like(request, postid):
    try:
        post = Post.objects.get(id=postid)
    except:
        return JsonResponse({"error": "Post not found."}, status=404)
    if request.method == 'PUT':
        data = json.loads(request.body)
        likeflag = data["flag"]
        if likeflag:
            post.likes.add(request.user)
        else:
            post.likes.remove(request.user)
        return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

@csrf_exempt
def follow(request, name):
    try:
        profileuser = User.objects.get(username=name)
    except:
        return JsonResponse({"error": "User not found."}, status=404)
    if request.method == 'PUT':
        data = json.loads(request.body)
        followflag = data["flag"]
        if followflag:
            profileuser.followers.add(request.user)
        else:
            profileuser.followers.remove(request.user)
        return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

def followings(request, name):
    try:
        follower = User.objects.get(username=name)
    except:
        return JsonResponse({"error": "User not found."}, status=404)
    followingposts = []
    for following in follower.followings.all():
        for post in following.posts.all():
            followingposts.append(post)
    def myFunc(post):
        return post.timestamp
    followingposts.sort(reverse=True, key=myFunc)
    return render(request, "network/followings.html", {"posts": paginate(request, followingposts)})