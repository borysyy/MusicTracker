from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, AuthenticationForm, CollectionForm
from .models import User, Collection

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
    current_user = request.user.get_username()
    collections = Collection.objects.filter(owner__username=username).order_by("name")
    collection_form = None

    if request.user == profile_user:
        collection_form = CollectionForm()

    context = {
        "profile_user": profile_user,
        "collections": collections,
        "current_user": current_user,
        "form": collection_form
    }
    
    
    return render(request, "core/base_profile.html", context)

def collection_view(request, username, code):
    
    collection = get_object_or_404(Collection, code=code)
    current_user = request.user.get_username()
    
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
        
