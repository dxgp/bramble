from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=50, blank=True)
    # TODO: Add profile picture

class Post(models.Model):
    user_id = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    text = models.TextField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.BigIntegerField()

class Follows(models.Model):
    follower = models.ForeignKey(AppUser, related_name='following', on_delete=models.CASCADE)
    followee = models.ForeignKey(AppUser, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followee')  # Ensure that a user can follow another user only once

    def __str__(self):
        return f"{self.follower} follows {self.followee}"
