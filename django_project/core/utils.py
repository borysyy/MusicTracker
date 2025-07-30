import os
import uuid
from django.apps import apps
from django.conf import settings
from django.shortcuts import get_object_or_404
from colorthief import ColorThief
from PIL import Image, ExifTags

# Get the dominant color of a profile picture
def get_image_hue(instance):
    """
    Extracts the dominant color from a user's profile picture.
    
    Args:
        instance: The user instance containing the profile picture.
    
    Returns:
        str: Hexadecimal representation of the dominant color.
    """
    try:
        # Ensure the image exists and retrieve the file path
        image_path = instance.profile_picture.path
        
        # Create a ColorThief object to analyze the image
        color_thief = ColorThief(image_path)
        dominant_color = color_thief.get_color(quality=1)  # Get dominant color
        
        # Convert RGB to hexadecimal format
        dominant_color = rgb_to_hex(*dominant_color)

        return dominant_color

    except Exception as e:
        print(f"Error processing hue for {instance.username}: {str(e)}")
        return "#000000"  # Default to black if an error occurs

def rgb_to_hex(r, g, b):
    """
    Converts RGB values to a hexadecimal color string.
    
    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).
    
    Returns:
        str: Hexadecimal representation of the color.
    """
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

# Generate a unique 5-digit code for each collection
def generate_unique_code():
    """
    Generates a unique 5-character alphanumeric code for a collection.
    
    Returns:
        str: A unique uppercase code.
    """
    Collections = apps.get_model("core", "Collection")
    while True:
        code = uuid.uuid4().hex[:5].upper()  # Generate a random 5-character code
        if not Collections.objects.filter(code=code).exists():
            return code  # Return if unique

# Resize and rename uploaded images
def rename_resize_images(instance, **kwargs):
    """
    Renames and resizes an image associated with an instance.
    
    Args:
        instance: The model instance containing the image field.
        **kwargs: 
            - image_field (str): Name of the image field in the model.
            - passedin_dir (str): Base directory for storing the image.
            - custom_path (callable or list, optional): Additional path components.
            - img_name (str): New name for the image (without extension).
            - max_size (tuple): Maximum size for resizing (width, height).
    
    Returns:
        None
    """
    try:
        image_field = kwargs.get("image_field")
        image_field_value = getattr(instance, image_field, None)

        # Ensure the image field is valid and retrieve the file path
        original_image = image_field_value.path
        if os.path.exists(original_image):
            # Open and convert image to RGB mode
            img = Image.open(original_image)
            
            # Correct orientation
            try:
                exif = img._getexif()
                if exif is not None:
                    orientation_key = next(
                        (key for key, value in ExifTags.TAGS.items() if value == "Orientation"),
                        None
                    )
                    if orientation_key is not None:
                        orientation = exif.get(orientation_key)
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
            except Exception as e:
                print(f"Could not correct image orientation: {e}")
                
            img = img.convert("RGB")

            # Get the directory where the image should be stored
            passedin_dir = kwargs.get("passedin_dir")
            custom_path = kwargs.get("custom_path", [])

            # Create a directory under MEDIA_ROOT
            if callable(custom_path):  
                custom_dir = os.path.join(settings.MEDIA_ROOT, passedin_dir, *custom_path(instance))
            else:
                custom_dir = os.path.join(settings.MEDIA_ROOT, passedin_dir)

            os.makedirs(custom_dir, exist_ok=True)  # Ensure directory exists

            # Construct new image name and path
            img_name = kwargs.get("img_name")
            img_name = f"{img_name}.jpg"
            absolute_dir = os.path.join(custom_dir, img_name)

            # Resize image to fit within max_size while maintaining aspect ratio
            max_size = kwargs.get("max_size")
            img.thumbnail(max_size)

            # Save the resized image
            img.save(absolute_dir, "JPEG")

            # Store the relative path in the image field
            relative_dir = os.path.relpath(absolute_dir, settings.MEDIA_ROOT)
            image_field_value.name = relative_dir


            # Remove the original image if it was renamed/moved
            if os.path.exists(original_image) and original_image != absolute_dir:
                os.remove(original_image)

    except Exception as e:
        print(f"Error processing image: {e}")

# Save or get an artist
def save_artist(artist):
    from .models import Artist

    user, uri, name, image = artist.values()
    artist_obj, _ = Artist.objects.get_or_create(
        user=user,
        uri=uri,
        defaults={"name": name, "image": image}
    )
    
    return artist_obj

# Save or get an album
def save_album(album):
    from .models import Album
    
    user, uri, title, release_year, cover_art, artist = album.values()
        
    album_obj, created = Album.objects.get_or_create(
        user=user,
        uri=uri,
        defaults={"title": title, "release_year": release_year, "cover_art": cover_art, "artist": artist}
    )
    
    return album_obj

# Actually save the artist or album in the selected collections from the frontend
def save_in_collection(type, obj, selected_collections):
    from .models import Collection
    
    collection_names = []
    
    for collection_code in selected_collections:
        collection = get_object_or_404(Collection, code=collection_code)
        save_attribute = getattr(collection, type)
        
        save_attribute.add(obj)
        name = getattr(collection, "name")
        
        collection_names.append(name)
        
    return collection_names
        
    