from django.urls import path
from .views import home_view, register_view

app_name = "core"

urlpatterns = [
    path("", home_view, name="home"),
    path("register", register_view, name="register")
]
