from django.contrib import admin
from .models import User, Collection

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "private", "profile_picture", "profile_hue")

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description", "date_created", "collection_type", "owner__username")
    