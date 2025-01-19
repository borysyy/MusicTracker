import os
import re
import uuid
from PIL import Image
from django.apps import apps
from django.conf import settings
from colorthief import ColorThief

def get_image_hue(instance):
    try:
        # Ensure the image exists and the path is correct
        image_path = instance.profile_picture.path
        
        # Create a ColorThief object from the image file
        color_thief = ColorThief(image_path)
        dominant_color = color_thief.get_color(quality=1)
        dominant_color = ", ".join(map(str, dominant_color))

        print(dominant_color)
        return dominant_color

    except Exception as e:
        print(f"Error processing hue for {instance.username}: {str(e)}")
        return "000,000,000" 


def generate_unique_code():
    Collections = apps.get_model("core", "Collection")
    while True:
        code = uuid.uuid4().hex[:5].upper()
        if not Collections.objects.filter(code=code).exists():
            return code

def rename_resize_images(instance, **kwargs):

    try:
        image_field = kwargs.get("image_field")
        image_field_value = getattr(instance, image_field, None)
        original_image = image_field_value.path
        if os.path.exists(original_image):

            # Open the original path
            img = Image.open(original_image)
            img = img.convert("RGB")

            # Make custom directory
            passedin_dir = kwargs.get("passedin_dir")
            custom_path = kwargs.get("custom_path", [])

            # Create the custom directory in /media/
            if callable(custom_path):  
                custom_dir = os.path.join(settings.MEDIA_ROOT, passedin_dir, *custom_path(instance))
            else:
                custom_dir = os.path.join(settings.MEDIA_ROOT, passedin_dir)

            os.makedirs(custom_dir, exist_ok=True)

            # Change image name
            img_name = kwargs.get("img_name")
            img_name = f"{img_name}.jpg"
            absolute_dir = os.path.join(custom_dir, img_name)

            # Resize image
            max_size = kwargs.get("max_size")
            img.thumbnail(max_size)

            img.save(absolute_dir, "JPEG")

            # Remove /media/ and store the relative path
            relative_dir = os.path.relpath(absolute_dir, settings.MEDIA_ROOT)
            image_field_value.name = relative_dir

            print(image_field_value.name)

            if os.path.exists(original_image) and original_image != absolute_dir:
                os.remove(original_image)
            

    except Exception as e:
        print(f"Error processing image: {e}")
