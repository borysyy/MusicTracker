from datetime import date
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Index

from .utils import generate_unique_code, rename_resize_images


class User(AbstractUser):
    """
    Custom user model with additional fields:
    - private: Whether the profile is private.
    - profile_picture: User's profile picture.
    - profile_hue: Dominant color of the profile picture.
    """
    private = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True
    )
    profile_hue = models.CharField(max_length=7, default="#000000")

    def save(self, *args, **kwargs):
        """Override save to resize and move profile pictures."""
        super().save(*args, **kwargs)

        if self.profile_picture and self.profile_picture.name != "profile_pictures/default_profile.jpg":
            rename_resize_images(
                self,
                image_field="profile_picture",
                passedin_dir="profile_pictures",
                custom_path=lambda x: [x.username],
                img_name=f"{self.username}_profile",
                max_size=(500, 500),
            )
            super().save(update_fields=["profile_picture"])

    def __str__(self):
        return self.username


class Genre(models.Model):
    """Represents a music genre."""
    genre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.genre


class Artist(models.Model):
    """Represents a music artist."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uri = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, db_index=True)
    image = models.URLField(null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['user', 'uri']

    def __str__(self):
        return self.name


class Album(models.Model):
    """Represents a music album."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uri = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    release_year = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    cover_art = models.URLField(null=True, blank=True)
    artist = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    class Meta:
        indexes = [
            Index(fields=["title"]),
            Index(fields=["artist", "release_year"])
        ]
        unique_together = ['user', 'uri']
        verbose_name = "Album"
        verbose_name_plural = "Albums"

    def __str__(self):
        return f"{self.title} by {self.artist}"


class Collection(models.Model):
    """
    Represents a collection of albums or artists owned by a user.
    """
    TYPE_CHOICES = [
        ("ALL", "All"),
        ("ALBUMS", "Albums"),
        ("ARTISTS", "Artists"),
    ]

    code = models.CharField(editable=False, max_length=5, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date_created = models.DateField(default=date.today)
    collection_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    thumbnail = models.ImageField(
        upload_to="collection_thumbnails/",
        default="collection_thumbnails/default_thumbnail.jpg",
        null=True,
        blank=True
    )
    albums = models.ManyToManyField(Album, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Override save to generate a unique code and resize thumbnails."""
        if not self.code:
            self.code = generate_unique_code()
                    
        super().save(*args, **kwargs)

        if self.thumbnail and self.thumbnail.name != "collection_thumbnails/default.jpg":
            rename_resize_images(
                self,
                image_field="thumbnail",
                passedin_dir="collection_thumbnails",
                custom_path=lambda x: [x.owner.username, x.code],
                img_name=f"{self.code.lower()}_collection",
                max_size=(500, 500),
            )
            super().save(update_fields=["thumbnail"])

    def __str__(self):
        return self.name


class FriendList(models.Model):
    """Represents a user's list of friends."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='friend_list')
    friends = models.ManyToManyField(User, blank=True, related_name='friend_of')

    def __str__(self):
        return f"{self.user.username}'s friends"

    def add_friend(self, account):
        """Add a mutual friendship."""
        if account != self.user and account not in self.friends.all():
            self.friends.add(account)
            self.save()
            friend_list = FriendList.objects.get(user=account)
            friend_list.friends.add(self.user)

    def remove_friend(self, account):
        """Remove a friend."""
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, account):
        """Remove mutual friendship."""
        account = User.objects.get(username=account)
        self.remove_friend(account)
        friend_list = FriendList.objects.get(user=account)
        friend_list.remove_friend(self.user)


class FriendRequest(models.Model):
    """Represents a friend request between two users."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"Friend request from {self.from_user.username} to {self.to_user.username} ({self.status})"
