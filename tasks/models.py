from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    # Organizer of the event
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )

    # Participants (RSVP)
    participant = models.ManyToManyField(
        User,
        related_name='rsvp_events',
        blank=True
    )

    # Event image with default
    image = models.ImageField(
        upload_to='event_images/',
        default='default_event.jpg'
    )

    # Optional: track creation/update times
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='userprofile', primary_key=True)
    profile_image = models.ImageField(upload_to='profile_images', blank=True, default='profile_images/default-image.jpg')
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} profile'
