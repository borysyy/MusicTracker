from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .forms import CustomUserCreationForm, AuthenticationForm, CollectionForm, ProfileUpdateForm
from .models import User, Collection, Artist, Album
from .utils import get_image_hue, save_artist, save_album, save_in_collection
from .spotify import get_results
from .serializers import UserSerializer, CollectionSerializer

# View for rendering the home page
def home_view(request):
    return render(request, "core/index.html")

# View for logging out a user
def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("core:home")

# View for handling user login
def login_view(request):
    context = {}
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            string = f"Successfully logged in as {user.username}"
            messages.success(request, string)
            return redirect("core:profile", user.username)
    else:
        form = AuthenticationForm()
    context = {"form": form}
    return render(request, "core/login.html", context)

# View for handling user registration
def register_view(request):
    context = {}
    if request.method == "POST":
        register_form = CustomUserCreationForm(data=request.POST, files=request.FILES)
        if register_form.is_valid():
            user = register_form.save()
            user.profile_hue = get_image_hue(user)
            user.save()

            login(request, user)
            string = f"Your account {user.username} has been created"
            messages.success(request, string)
            return redirect("core:profile", user.username)
    else:
        register_form = CustomUserCreationForm()
        
    context = {"form": register_form}
    return render(request, "core/register.html", context)

# View for displaying user profiles
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    current_user = request.user
    collections = Collection.objects.filter(owner__username=username).order_by("name")
    collection_form = None
    update_form = None
        
    if current_user == profile_user:
        collection_form = CollectionForm()
        update_form = ProfileUpdateForm(instance=current_user)
        
    context = {
        "profile_user": profile_user,
        "collections": collections,
        "current_user": current_user,
        "collection_form": collection_form,
        "update_form": update_form
    }
    
    return render(request, "core/base_profile.html", context)

# View for displaying a specific collection
def collection_view(request, username, code):
    collection = get_object_or_404(Collection, code=code)
    current_user = request.user
    update_form = None
    
    if current_user.username == collection.owner.username:
        update_form = CollectionForm(instance=collection)
    
    artists = collection.artists.all().order_by('name')
    for artist in artists:
        artist.uri_last_part = artist.uri.split(':')[-1]
        
    collection.artists_list = artists

    albums = collection.albums.all().order_by('title')
    for album in albums:
        album.uri_last_part = album.uri.split(':')[-1]
        
    collection.albums_list = albums
    
    

    context = {
        "collection": collection,
        "current_user": current_user,
        "update_form": update_form
    }
    return render(request, "core/collection.html", context)

# View for adding a new collection
def add_collection_view(request, username):
    owner = get_object_or_404(User, username=username)
    if request.method == "POST":
        collection_form = CollectionForm(data=request.POST, files=request.FILES)
        if collection_form.is_valid():
            collection = collection_form.save(commit=False)
            collection.owner = owner
            collection.save()
            code = collection.code
            
            string = f"Your collection {collection.name} has been created"
            messages.success(request, string)
            
            return redirect("core:collection", username, code)
        else:
            print("form.errors:\n", collection_form.errors)


def search_view(request):
    if request.method == "POST":
        user_input = request.POST.get("input", "")
        
        top_results, album_results, artist_results = get_results(user_input)
        
        context = {
            "topResult": top_results, 
            "albumResults": album_results, 
            "artistResults": artist_results
            }

        return JsonResponse(context)
    else:
        collections = Collection.objects.filter(owner__username = request.user.username)
        
        context = {
            "user_collections": collections
        }
        return render(request, "core/search.html", context)
        
# API view for updating user information
class UserUpdate(APIView):
    def put(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        with transaction.atomic():
            if serializer.is_valid():
                serializer.save()
                username = serializer.data['username']
                
                redirect_url = reverse("core:profile", kwargs={"username": username})
                return Response({"redirect_url": redirect_url})
            else:
                return Response(serializer.errors, status=400)

# API view for updating a collection
class CollectionUpdate(APIView):
    def put(self, request, username, code):
        collection = get_object_or_404(Collection, code=code)
        serializer = CollectionSerializer(collection, data=request.data, partial=True)
        
        with transaction.atomic():
            if serializer.is_valid():
                serializer.save()
                
                username = request.user.username
                code = collection.code
                
                redirect_url = reverse("core:collection", kwargs={"username": username, "code": code})
                return Response({"redirect_url": redirect_url})
            else:
                return Response(serializer.errors, status=400)

class SaveToCollection(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        print(request.data)
        
        user = request.user
        music_type = request.data["type"]
        selected_collections = request.data["selected_collections"]
        uri = request.data["uri"]
        
        if not selected_collections:
            return Response({"error": "No Collection Selected"}, status=400)

        if music_type == "artist":
            name = request.data["name"]
            image = request.data["image"]
            artist_data = {
                "user": user,
                "uri": uri,
                "name": name,
                "image": image
            }
           
            artist_obj = save_artist(artist_data)
            
            collections = save_in_collection(type="artists", obj=artist_obj, selected_collections=selected_collections)
            
            return Response({"success": f"{music_type.capitalize()}, {name} saved to {', '.join(collections)}"}, status=200)
        elif music_type == "album":
            title = request.data["title"]
            release_year = request.data["release_year"]
            cover_art = request.data["cover_art"]
            artist = request.data["artist_name"]
            
            album_data = {
                "user": user,
                "uri": uri,
                "tile": title,
                "release_year": release_year,
                "cover_art": cover_art,
                "artist": artist
            }
            
            album_obj = save_album(album_data)
            
            collections = save_in_collection(type="albums", obj=album_obj, selected_collections=selected_collections)
            
            return Response({"success": f"{music_type.capitalize()}, {title} saved to {', '.join(collections)}"}, status=200)
        
        
        
        return Response({"error": "Invalid request"}, status=400)
            
    