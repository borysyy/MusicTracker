from django.urls import path
from .views import (
    home_view, register_view, login_view, logout_view, profile_view, 
    collection_view, add_collection_view, search_view, add_friends_view ,UserUpdate, CollectionUpdate, SaveToCollection, DeleteFromCollection
)

app_name = "core"

urlpatterns = [
    path("", home_view, name="home"),
    path("register", register_view, name="register"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("profile/<str:username>", profile_view, name="profile"),
    path("profile/<str:username>/update", UserUpdate.as_view(), name="update_profile"),
    path("profile/<str:username>/collection/update", add_collection_view, name="add_collection"),
    path("profile/<str:username>/collection/<str:code>", collection_view, name="collection"),
    path("profile/<str:username>/collection/<str:code>/update", CollectionUpdate.as_view(), name="update_collection"),
    path("profile/<str:username>/collection/<str:code>/delete/<str:type>/<str:music>", DeleteFromCollection.as_view(), name="delete_music"),
    path("save", SaveToCollection.as_view(), name="save"),
    path("search", search_view, name="search"),
    path("add-friends", add_friends_view, name="add_friends")
]