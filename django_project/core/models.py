import os
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

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
    
    # Save profile picture to user directory
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)  # Save to get a valid file path
        
        # Process profile picture before saving
        if self.profile_picture and self.profile_picture.name != 'profile_pictures/default_profile.jpg':
            original_image = self.profile_picture.path
            print(f"Image path: {original_image}")

            if os.path.exists(original_image):
                try:
                    img = Image.open(original_image)
                    img = img.convert("RGB")

                    # Create user directory
                    user_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pictures', self.username)
                    os.makedirs(user_dir, exist_ok=True)

                    # Save the processed image
                    new_img_name = f"{self.username}_profile.jpg"
                    new_img_abs_path = os.path.join(user_dir, new_img_name)
                    img.save(new_img_abs_path, "JPEG")

                    # Update profile picture path
                    new_img_rel_path = os.path.join('profile_pictures', self.username, new_img_name)
                    self.profile_picture.name = new_img_rel_path
                    print(self.profile_picture.name)

                    # Remove old image if it exists and is not the new image
                    if os.path.exists(original_image) and original_image != new_img_abs_path:
                        os.remove(original_image)
                        
                    super().save(update_fields=["profile_picture"])


                except Exception as e:
                    print(f"Error processing profile picture: {e}")

        super().save(*args, **kwargs)
