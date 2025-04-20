from colorfield.fields import ColorField
from datetime import date
from PIL import Image
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Index
from django.conf import settings
from django.core.exceptions import ValidationError
from .utils import generate_unique_code, rename_resize_images


# Custom User model extending Django's AbstractUser
class User(AbstractUser):
    """
    Custom user model with additional fields:
    - private: Boolean field indicating if the profile is private.
    - profile_picture: Image field for storing the user's profile picture.
    - profile_hue: Hex color code representing the dominant color of the profile picture.
    """
    private = models.BooleanField(default=False)  # Determines if profile is private

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",  # Directory where images are stored
        default="profile_pictures/default_profile.jpg",  # Default profile picture
        null=True, 
        blank=True
    )

    profile_hue = models.CharField(max_length=7, default="#000000")  # Stores dominant profile picture color
    
    def save(self, *args, **kwargs):
        """
        Overrides the default save method to process the profile picture:
        - Ensures the image is resized and stored in a user-specific directory.
        """
        super().save(*args, **kwargs)  # Save to get a valid file path
        
        # Process the profile picture if it's not the default image
        if self.profile_picture and self.profile_picture.name != "profile_pictures/default_profile.jpg":
            rename_resize_images(self, 
                                 image_field="profile_picture",
                                 passedin_dir="profile_pictures",
                                 custom_path=lambda x: [x.username],  # Store in a user-specific directory
                                 img_name=f"{self.username}_profile",  # Rename image
                                 max_size=(500, 500),  # Resize to a max of 500x500
                                 )
                        
        super().save(update_fields=["profile_picture"])  # Save only the updated profile picture
        
    def __str__(self):
        return self.username 
    

# Genre model to categorize music
class Genre(models.Model):
    """
    Represents a music genre.
    - genre: The name of the genre (unique).
    """
    genre = models.CharField(max_length=255, unique=True)  # Genre name must be unique

    def __str__(self):
        return self.genre  # String representation


# Artist model storing artist details
class Artist(models.Model):
    """
    Represents a music artist.
    - uri: Unique identifier for external integrations (optional).
    - name: Artist's name, indexed for efficient lookups.
    - image: URL of the artist's image (optional).
    - genre: ForeignKey linking to a Genre.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Owner of this artist
    uri = models.CharField(max_length=255, null=True, blank=True)  # External reference
    name = models.CharField(max_length=255, db_index=True)  # Indexed for faster queries
    image = models.URLField(null=True, blank=True)  # Optional image URL
    
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)  # Artist's genre

    class Meta:
        unique_together = ['user', 'uri']

    def __str__(self):
        return self.name  # String representation


# Album model storing album details
class Album(models.Model):
    """
    Represents a music album.
    - title: Album title.
    - release_year: Year of release (must be non-negative).
    - cover_art: URL to album cover image (optional).
    - genre: ForeignKey linking to Genre.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uri = models.CharField(max_length=255, null=True, blank=True)  # External reference
    title = models.CharField(max_length=255)  # Album title
    release_year = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])  # Non-negative release year
    cover_art = models.URLField(null=True, blank=True)  # Optional album cover image URL
    
    artist = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)  # Genre can be null

    class Meta:
        indexes = [
            Index(fields=["title"]),  # Indexing title for faster searches
            Index(fields=["artist", "release_year"])  # Indexing artist and release year for optimized queries
        ]

        unique_together = ['user', 'uri']
        verbose_name = "Album"
        verbose_name_plural = "Albums"
    
    def __str__(self):
        return f"{self.title} by {self.artist}"  # String representation


# Collection model to group albums and artists
class Collection(models.Model):
    """
    Represents a collection of albums or artists owned by a user.
    - code: Unique identifier for the collection.
    - name: Collection name.
    - description: Optional text description.
    - date_created: Auto-filled creation date.
    - collection_type: Indicates if the collection is for albums or artists.
    - thumbnail: Image field for collection preview.
    - albums: Many-to-Many relationship with Album.
    - artists: Many-to-Many relationship with Artist.
    - owner: ForeignKey linking to User.
    """
    TYPE_CHOICES = [
        ("ALL", "All"),
        ("ALBUMS", "Albums"),
        ("ARTISTS", "Artists"),
    ]

    code = models.CharField(editable=False, max_length=5, primary_key=True)  # Unique code for identification
    name = models.CharField(max_length=255)  # Collection name
    description = models.TextField(null=True, blank=True)  # Optional collection description
    date_created = models.DateField(default=date.today)  # Automatically set the creation date
    collection_type = models.CharField(max_length=50, choices=TYPE_CHOICES)  # Type of collection (albums or artists)
    
    thumbnail = models.ImageField(
        upload_to="collection_thumbnails/",  # Directory for storing collection thumbnails
        default="collection_thumbnails/default_thumbnail.jpg",
        null=True, 
        blank=True
    )

    albums = models.ManyToManyField(Album, blank=True)  # A collection can have multiple albums
    artists = models.ManyToManyField(Artist, blank=True)  # A collection can have multiple artists
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # Collection belongs to a user

    def save(self, *args, **kwargs):
        """
        Overrides the save method to:
        - Generate a unique code if not already assigned.
        - Resize and store collection thumbnails.
        """
        if not self.code:
            self.code = generate_unique_code()  # Assign a unique code if not set
                    
        super().save(*args, **kwargs)  # Save instance to generate a valid file path

        # Process collection thumbnail if it's not the default image
        if self.thumbnail and self.thumbnail.name != "collection_thumbnails/default.jpg":
            rename_resize_images(self, 
                                 image_field="thumbnail",
                                 passedin_dir="collection_thumbnails", 
                                 custom_path=lambda x: [x.owner.username, x.code],  # Store under owner's directory
                                 img_name=f"{self.code.lower()}_collection",  # Rename image
                                 max_size=(500, 500),  # Resize to a max of 500x500
                                 )
          
            super().save(update_fields=["thumbnail"])  # Save only the updated thumbnail

    def __str__(self):
        return self.name  # String representation

class FriendList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='friend_list')
    friends = models.ManyToManyField(User, blank=True, related_name='friend_of')
    
    def __str__(self):
        return f"{self.user.username}'s friends"
    
    def add_friend(self, account):
        if account != self.user and account not in self.friends.all():
            self.friends.add(account)
            self.save()
            friend_list, created = FriendList.objects.get_or_create(user=account)
            friend_list.friends.add(self.user)
    
    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
            
    def unfriend(self, account):
        account = User.objects.get(username=account)
        
        self.remove_friend(account)
        
        friend_list = FriendList.objects.get(user=account)
        friend_list.remove_friend(self.user)

class FriendRequest(models.Model):
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
        return f"Friend request from {self.from_user.username} to {self.to_user.username} is {self.status}"

