from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Bid(models.Model):
    bidder = models.CharField(max_length=64, default="anon")
    bidPrice = models.IntegerField(default=0)

    def __str__(self):
        return f"${self.bidPrice} (Bid by '{self.bidder}')"

class Comment(models.Model):
    username = models.CharField(max_length=64)
    commentTime = models.DateTimeField(default=timezone.now)
    comment = models.CharField(max_length=256, default="")
    # post = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="commentedPost", null=True)

    def __str__(self):
        return f"{self.username}: {self.comment}"


class Auction(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    price = models.IntegerField(default=0)
    imageLink = models.URLField(blank=True)
    op = models.CharField(max_length=64)
    category_choices = [
        ("Food", "Food"),
        ("Alcohol", "Alcohol"),
        ("Books", "Books"),
        ("Music", "Music"),
        ("Tech", "Tech"),
    ]
    category = models.CharField(max_length=10, choices=category_choices, blank=True)
    comments = models.ManyToManyField(Comment, blank=True, related_name="comments")
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name="itemBid", null=True, blank=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} at ${self.price}"


class User(AbstractUser):
    watchList = models.ManyToManyField(
        Auction, blank=True, related_name="watchers"
    )

