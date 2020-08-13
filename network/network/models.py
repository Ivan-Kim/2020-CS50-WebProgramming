from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    followers = models.ManyToManyField("self", blank=True, related_name="followings", symmetrical=False)

class Comment(models.Model):
    username = models.CharField(max_length=64)
    commentTime = models.DateTimeField(default=timezone.now)
    comment = models.CharField(max_length=256, default="")

    def __str__(self):
        return f"{self.username}: {self.comment}"

class Post(models.Model):
    op = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.CharField(max_length=256)
    timestamp = models.DateTimeField(default=timezone.now)
    comments = models.ManyToManyField(Comment, related_name="commentedPosts", blank=True)
    likes = models.ManyToManyField(User, related_name="likedPosts", blank=True)
