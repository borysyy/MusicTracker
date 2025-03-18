from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .forms import CustomUserCreationForm, AuthenticationForm, CollectionForm, ProfileUpdateForm
from .models import User, Collection
from .utils import get_image_hue
from .serializers import UserSerializer

# Create your views here.
def home_view(request):
    return render(request, "core/index.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("core:home")

def login_view(request):
    context = {}
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            string = f"Sucessfully logged in as {user.username}"
            messages.success(request, string)
            return redirect("core:profile", user.username)
    else:
        form = AuthenticationForm()
    context = {"form": form}
    return render(request, "core/login.html", context)

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

def collection_view(request, username, code):

    collection = get_object_or_404(Collection, code=code)
    current_user = request.user
    
    context = {
        "collection": collection,
        "current_user": current_user
    }
    return render(request, "core/collection.html", context)


def update_collection_view(request, username):
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
        

class UserUpdate(APIView):
    def put(self, request, username):
        
        user = get_object_or_404(User, username=username)
        serializer = UserSerializer(user, data=request.data, partial=True)
            
        if serializer.is_valid():
            serializer.save()
            username = serializer.data['username']
            
            redirect_url = reverse("core:profile", kwargs={"username":username})
            return Response({"redirect_url":redirect_url})
        else:
            return Response(serializer.errors, status=400)
