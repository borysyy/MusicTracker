from django.urls import path
from .views import (
    home_view, register_view, login_view, logout_view, profile_view, 
    collection_view, add_collection_view, search_view, search_friends_view, 
    get_current_requests_view, 
    UserUpdate, CollectionUpdate, SaveToCollection, DeleteFromCollection,
    RequestFriendView, CancelFriendRequestView, AcceptFriendRequestView, 
    RejectFriendRequestView, RemoveFriendView,
)

app_name = "core"

urlpatterns = [
    # Basic Urls
    path("", home_view, name="home"),
    path("register", register_view, name="register"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    
    # Urls for user profile pages
    path("profile/<str:username>", profile_view, name="profile"),
    path("profile/<str:username>/update", UserUpdate.as_view(), name="update_profile"),
    path("profile/<str:username>/collection/add", add_collection_view, name="add_collection"),
    path("profile/<str:username>/collection/<str:code>", collection_view, name="collection"),
    path("profile/<str:username>/collection/<str:code>/update", CollectionUpdate.as_view(), name="update_collection"),
    path("profile/<str:username>/collection/<str:code>/delete/<str:type>/<str:music>", DeleteFromCollection.as_view(), name="delete_music"),
    
    # Urls for searching and saving music
    path("search", search_view, name="search"),
    path("save", SaveToCollection.as_view(), name="save"),
    
    # Urls for friend feature
    path("add-friends", search_friends_view, name="add_friends"),
    path("current-requests", get_current_requests_view, name="current_requests"),
    path("request-friend/<str:username>", RequestFriendView.as_view(), name="requesting_friend"),
    path("cancel-request/<str:username>", CancelFriendRequestView.as_view(), name="cancel_friend_request"),
    path("accept-request/<str:username>", AcceptFriendRequestView.as_view(), name="accept_friend_request"),
    path("reject-request/<str:username>", RejectFriendRequestView.as_view(), name="reject_friend_request"),
    path("remove-friend/<str:username>", RemoveFriendView.as_view(), name="removing_friend"),
    
]