from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, AuthenticationForm
from .models import User

# Create your views here.
def home_view(request):
    return render(request, "core/index.html")

def logout_view(request):
    logout(request)
    return redirect("core:home")

def login_view(request):
    context = {}
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("core:profile", user.username)
    else:
        form = AuthenticationForm()
    context = {"form": form}
    return render(request, "core/login.html", context)

def register_view(request):
    context = {}
    if request.method == "POST":
        form = CustomUserCreationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created")
            return redirect("core:home")
    else:
        form = CustomUserCreationForm()
        
    context = {"form": form}
    return render(request, "core/register.html", context)

def profile_view(request, username):
    
    user = get_object_or_404(User, username=username)
    
    current_user = request.user.get_username()
    
    context = {
        'user': user,
        'current_user': current_user
    }
    
    
    return render(request, "core/base_profile.html", context)