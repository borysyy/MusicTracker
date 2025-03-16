from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, AuthenticationForm, CollectionForm, ProfileUpdateForm
from .models import User, Collection
from .utils import get_image_hue
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
        print(register_form)
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
        print(request.data)
        
        user = get_object_or_404(User, username=username)
        serializer = UserSerializer(user, data=request.data, partial=True)
            
        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data)
        else:
            return redirect("core:profile", username=username)

            

def update_profile_view(request, username):    
    if request.method == "POST":
        user = request.user
        update_form = ProfileUpdateForm(data=request.POST, files=request.FILES)
        if update_form.is_valid():
            new_username = update_form.cleaned_data["username"]
            new_first_name = update_form.cleaned_data["first_name"]
            new_privacy = update_form.cleaned_data["private"]
            new_profile_picture = update_form.cleaned_data["profile_picture"]
            
            if new_username != user.username:
                if User.objects.filter(username=new_username).exists():
                    messages.error(request, 'A user with that username already exists.')
                    return redirect("core:profile", username=username)  # Fix redirect to pass correct username
            
            user.username = new_username
            user.first_name = new_first_name
            user.private = new_privacy
            if new_profile_picture:
                user.profile_picture = new_profile_picture
            user.save()
            
            
            string = "Your profile has been updated"
            messages.success(request, string)
            return redirect("core:profile", username=user.username)
        else:
            print("form.errors:\n", update_form.errors)
            return JsonResponse("Empty", safe=False)
 