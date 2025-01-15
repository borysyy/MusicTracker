from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, AuthenticationForm

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
            return redirect("core:home")
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