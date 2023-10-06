from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("self", symmetrical=False, related_name="following")

    def __str__(self):
        return f"({self.id}) {self.username}"


class Post(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)

    def __str__(self):
        return f"({self.timestamp.strftime('%I:%M:%S %p')}) {self.user}: '{self.content}'"
    
    def count_likes(self):
        return self.likes.count()
    
    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "user": self.user.username,
            "content": self.content
        }


class Like(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user.username} liked {self.post}"
    
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "post": self.post.id
        }