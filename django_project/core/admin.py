from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Collection

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "private", "profile_picture", "profile_hue")

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description", "date_created", "collection_type", "owner__username", "thumbnail")
    fieldsets = [
        ("Name/Type", {"fields": ["name", "collection_type"]}),
        ("Description", {"fields": ["description"]}),
        ("Thumbnail", {"fields": ["thumbnail"]})
    ]
    
    
    def save_model(self, request, obj, form, change):
        try:
            if not obj.owner:  # Check if the owner is not set
                obj.owner = request.user
        except ObjectDoesNotExist:
            # Handling the case where the owner is not assigned yet
            obj.owner = request.user
        super().save_model(request, obj, form, change)
