from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm

# Create your views here.
def home_view(request):
    return render(request, "core/index.html")

# def login_view(request):
#     if request.method == "POST":
#         form =

def register_view(request):
    context = {}
    if request.method == "POST":
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created")
            return redirect('core:home')
    else:
        form = CustomUserCreationForm()
        
    context = {"form": form}
    return render(request, "core/register.html", context)