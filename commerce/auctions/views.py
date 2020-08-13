from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from .models import User, Auction, Bid, Comment

class listForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = "__all__"
        labels = {
            "imageLink": "(Optional) URL Link for product image",
            "category": "(Optional) Category of product",
        }
        exclude = ('closed', 'comments', 'bid',)
        widgets = {'op': forms.HiddenInput(),}

class commentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"
        labels = {"comment": ""}
        widgets = {'comment': forms.Textarea(), 'commentTime': forms.HiddenInput(), 'username': forms.HiddenInput()}

class bidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = "__all__"
        labels = {"bidPrice": "Place your bid"}
        widgets = {'bidder': forms.HiddenInput()}

def index(request):
    return render(request, "auctions/index.html", {"lists": Auction.objects.all()})


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        form = listForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/createList.html", {"form": form})
    return render(request, "auctions/createList.html", {"form": listForm(initial={'op': request.user})})


def item(request, item):
    # check if item exists in database else render error
    try:
        product = Auction.objects.get(name=item)
    except:
        return render(request, "auctions/error.html")
    # when user submits either bid or comment
    if request.method == "POST":
        comment = commentForm(request.POST)
        bid = bidForm(request.POST)
        # when post comment on the item page
        if comment.is_valid():
            comment = comment.save()
            # add the posted comment to the product's comment list
            product.comments.add(comment)
            return HttpResponseRedirect(reverse("item", args=(item,)))
        # when post bid on the item page
        elif bid.is_valid():
            # check if bid is higher than current price
            if bid.cleaned_data["bidPrice"] > product.price:
                bid = bid.save()
                product.bid = bid
                product.price = bid.bidPrice
                # update the product with new bid and its price
                product.save(update_fields=["bid", "price"])
                return HttpResponseRedirect(reverse("item", args=(item,)))
            else:
                messages.error(request, "Bid must be higher than the current bid")
                return HttpResponseRedirect(reverse("item", args=(item,)))
        else:
            return render(request, "auctions/error.html")
    # when user views the item page by clicking
    else:
        return render(
            request,
            "auctions/item.html",
            {"item": product, 
            "bidform": bidForm(initial={'bidder': request.user, 'bidPrice': product.bid}),
            "commentform": commentForm(initial={'username': request.user})},
        )

def watch(request, item):
    product = Auction.objects.get(name=item)
    watchlist = request.user.watchList
    if product not in watchlist.all():
        watchlist.add(product)
    else:
        watchlist.remove(product)
    return render(request, "auctions/watchlist.html")


@login_required(login_url='login')
def watchlist(request):
    return render(request, "auctions/watchlist.html")


def categories(request):
    allCategories = []
    for item in Auction.objects.all():
        if item.category not in allCategories:
            allCategories.append(item.category)
        else:
            continue
    return render(request, "auctions/categories.html", {"categories": allCategories})


def categoryitems(request, category):
    allItems = Auction.objects.filter(category=category)
    return render(request, "auctions/categoryitems.html", {"items": allItems})

def close(request, item):
    product = Auction.objects.get(name=item)
    product.closed = True
    product.save(update_fields=["closed"])
    return HttpResponseRedirect(reverse("item", args=(item,)))
