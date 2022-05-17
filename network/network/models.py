from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Posts(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%d %b %Y, %I:%M %p"),
            "likes": self.likes
        }

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="are_liking")
    posts = models.ManyToManyField(Posts, blank=False, related_name="likers")

class Follows(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="are_following")
    follows = models.ManyToManyField(User, blank=False, related_name="followers")

    def __str__(self):
        return f"{self.user} follows: {self.follows}."


"""
User.are_following -> shows that user actually follows somebody, that he is in model
User.followers -> shows which users are followed by this user
"""