from colorfield.fields import ColorField
from datetime import date
from PIL import Image
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Index
from .utils import generate_unique_code, rename_resize_images, get_image_hue




# Create your models here.

# Custom fields for user model
class User(AbstractUser):
    # Private profile
    private = models.BooleanField(default=False) 

    # Profile Picture
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", 
        default="profile_pictures/default_profile.jpg", 
        null=True, 
        blank=True
    )

    # Profile Hue
    profile_hue = ColorField(default="000,000,000")
    
    # Save profile picture to user directory
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)  # Save to get a valid file path
        
        # Process profile picture before saving
        if self.profile_picture and self.profile_picture.name != "profile_pictures/default_profile.jpg":
            rename_resize_images(self, 
                                 image_field = "profile_picture",
                                 passedin_dir="profile_pictures",
                                 custom_path=lambda x: [x.username],
                                 img_name=f"{self.username}_profile", 
                                 max_size=(500,500), 
                                 )
                        
            super().save(update_fields=["profile_picture"])

            self.profile_hue = get_image_hue(self)
            super().save(update_fields=["profile_hue"])


class Genre(models.Model):
    genre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.genre

class Artist(models.Model):
    uri = models.CharField(max_length=255, unique=True ,null=True, blank=True)
    name = models.CharField(max_length=255, db_index=True)
    image = models.URLField(null=True, blank=True)
    
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
class Album(models.Model):
    title = models.CharField(max_length=255)
    release_year = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    cover_art = models.URLField(null=True, blank=True)
    
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    class Meta:
        indexes = [
            Index(fields=["title"]),
            Index(fields=["artist", "release_year"])
        ]

        unique_together = ("title", "artist")
        verbose_name = "Album"
        verbose_name_plural = "Albums"
    
    def __str__(self):
        return f"{self.title} by {self.artist.name}"


class Collection(models.Model):
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
        if not self.code:
            self.code = generate_unique_code()
                    
        super().save(*args, **kwargs)

        if self.thumbnail and self.thumbnail.name != "collection_thumbnails/default.jpg":
            rename_resize_images(self, 
                                 image_field = "thumbnail",
                                 passedin_dir="collection_thumbnails", 
                                 custom_path=lambda x: [x.owner.username, x.code],
                                 img_name=f"{self.code.lower()}_collection",
                                 max_size=(300,300), 
                                 )
          
            super().save(update_fields=["thumbnail"])


    def __str__(self):
        return self.name