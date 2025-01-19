from django.urls import path
from .views import home_view, register_view, login_view, logout_view, profile_view, collection_view

app_name = "core"

urlpatterns = [
    path("", home_view, name="home"),
    path("register", register_view, name="register"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("profile/<str:username>", profile_view, name="profile"),
    path("profile/<str:username>/collection/<str:code>", collection_view, name="collection")
]
