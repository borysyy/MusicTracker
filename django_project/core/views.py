from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CustomUserCreationForm, AuthenticationForm, CollectionForm, ProfileUpdateForm
from .models import User, Collection, FriendList, FriendRequest
from .serializers import UserSerializer, CollectionSerializer, CollectionSaveSerializer
from .spotify import get_results
from .utils import get_image_hue

# View for rendering the home page
def home_view(request):
    if request.user.is_authenticated:
        return redirect("core:profile", request.user.username)
    else:
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
    
    if request.user.is_authenticated:
        return redirect("core:profile", request.user.username)
    else:
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
    
    if request.user.is_authenticated:
        return redirect("core:profile", request.user.username)
    else:
        return render(request, "core/register.html", context)

# View for displaying user profiles
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    current_user = request.user
    collections = Collection.objects.filter(owner__username=username).order_by("-date_created")
    friends_list = FriendList.objects.get(user=profile_user)
    friends = friends_list.friends.all()
    sent_requests = FriendRequest.objects.filter(from_user=profile_user, status="pending")
    received_requests = FriendRequest.objects.filter(to_user=profile_user, status="pending")
    received_requests_count = received_requests.count()
    collection_form = None
    update_form = None

        
    if current_user == profile_user:
        collection_form = CollectionForm()
        update_form = ProfileUpdateForm(instance=current_user)
        
    context = {
        "profile_user": profile_user,
        "collections": collections,
        "friends": friends,
        "sent_requests": sent_requests,
        "received_requests": received_requests,
        "received_requests_count": received_requests_count,
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

# View for adding a new collection (requires login)
@login_required
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

# View for handling Spotify search and displaying results (requires login)
@login_required
def search_view(request):
    current_user = request.user
    collection_form = CollectionForm()

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
            "user_collections": collections,
            "collection_form": collection_form,
            "current_user": current_user
        }
        return render(request, "core/search.html", context)

# View for searching for other users to add as friends (requires login)
@login_required
def search_friends_view(request):
    if request.method == "POST":
        user_input = request.POST.get("input", "")
        
        users = User.objects.filter(
            Q(username__icontains=user_input) | Q(first_name__icontains=user_input),
            private=False
        ).exclude(username=request.user.username).all()[:20]
        
        user_dict = {
            "users": [
                {
                    "username": u.username,
                    "first_name": u.first_name,
                    "profile_picture": request.build_absolute_uri(u.profile_picture.url),
                    "private": u.private
                }
                for u in users
            ]
        }
                        
        return JsonResponse(user_dict)
    else:
        return render(request, "core/add_friends.html")

# View for getting the current user's friend request data (requires login)
@login_required
def get_current_requests_view(request):
    outgoing_requests = list(FriendRequest.objects.filter(from_user=request.user, status="pending").values("to_user__username"))
    incoming_requests = list(FriendRequest.objects.filter(to_user=request.user, status="pending").values("from_user__username"))
    accepted_requests = list(FriendList.objects
        .filter(user=request.user)
        .exclude(friends__username__isnull=True)
        .values("friends__username")
    )
    

    
    requests_dict = {
        "outgoing_requests": outgoing_requests, 
        "incoming_requests": incoming_requests,
        "accepted_requests": accepted_requests
    }

    return JsonResponse(requests_dict)
        
# API view for updating user information
class UserUpdate(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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

# API view for saving music to a collection
class SaveToCollection(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CollectionSaveSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            obj = result["object"]
            names = result["saved_to"]
            return Response({
                "success": f"{request.data['type'].capitalize()}, {getattr(obj, 'name', getattr(obj, 'title', ''))} saved to {', '.join(names)}"
            }, status=200)
        return Response(serializer.errors, status=400)

# API view for deleting music from a collection
class DeleteFromCollection(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, username, code, type, music):
        collection = Collection.objects.get(code=code)
        
        if type == "albums":
            album = collection.albums.filter(title__iexact=music).first()
            if album:
                collection.albums.remove(album)
        elif type == "artists":
            artist = collection.artists.filter(name__iexact=music).first()
            if artist:
                collection.artists.remove(artist)
                
        redirect_url = reverse("core:collection", kwargs={"username": username, "code": code})
        return Response({"redirect_url": redirect_url})

# Sending a friend request
class RequestFriendView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, username):
        now = timezone.now()
        friend = get_object_or_404(User, username=username)
        new_request = FriendRequest.objects.create(from_user=request.user, to_user=friend, created_at=now)
        return Response({'success': f'{friend.username} requested as a friend.'})

# Canceling a friend request
class CancelFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, username):
        friend = get_object_or_404(User, username=username)
        old_request = FriendRequest.objects.get(from_user=request.user, to_user=friend)
        old_request.delete()
        return Response({'success': f'Friend request to {friend.username} canceled'})
    
# Accepting a friend request
class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, username):
        friend = get_object_or_404(User, username=username)
        accepted_request = FriendRequest.objects.get(from_user=friend, to_user=request.user)
        accepted_request.status = "accepted"
        accepted_request.save()
        friends_list = FriendList.objects.get(user=request.user)
        friends_list.add_friend(friend)
        return Response({'success': f'Frend request from {friend.username} accepted'})

# Rejecting a friend request
class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, username):
        friend = get_object_or_404(User, username=username)
        current_request = FriendRequest.objects.get(from_user=friend, to_user=request.user)
        current_request.delete()
        return Response({'success': f'Friend request from {friend.username} rejected'})

# Removing a friend
class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, username):
        friend = get_object_or_404(User, username=username)
        accepted_request = FriendRequest.objects.get(
            (Q(from_user=friend, to_user=request.user) | Q(from_user=request.user, to_user=friend)) &
            Q(status="accepted")
        )
        accepted_request.delete()
        friend_list = FriendList.objects.get(user=request.user)
        friend_list.unfriend(username)
        return Response({'success': f'{username} is removed as a friend.'})
        