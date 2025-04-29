from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import User, Collection, Artist, Album


# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'private', 'profile_picture', 'profile_hue']
        
    def update(self, instance, validated_data):
        # If no new profile picture is provided, retain the existing one
        if validated_data["profile_picture"] is None:
            validated_data["profile_picture"] = instance.profile_picture
        
        # Check if the username is being changed and if the new one is already taken
        new_username = validated_data.get("username", instance.username)
        if new_username != instance.username and User.objects.filter(username=new_username).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        
        # Toggle the privacy setting if the user has checked the box in the frontend
        if validated_data["private"] == True:
           validated_data["private"] = not instance.private

        return super().update(instance, validated_data)

# Serializer for the Collection model
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'collection_type', 'thumbnail']
        
    def update(self, instance, validated_data):
        print(validated_data)  # Debugging output to inspect incoming data
        
        # If no new thumbnail is provided, retain the existing one
        if validated_data["thumbnail"] is None:
            validated_data["thumbnail"] = instance.thumbnail
        
        return super().update(instance, validated_data)

# Serializer for the Artist Model
class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['uri', 'name', 'image']

    def create(self, validated_data):
        user = self.context['request'].user
        artist, _ = Artist.objects.get_or_create(
            user=user,
            uri=validated_data['uri'],
            defaults={
                'name': validated_data['name'],
                'image': validated_data['image']
            }
        )
        return artist

# Serializer for the Album Model
class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['uri', 'title', 'release_year', 'cover_art', 'artist']

    def create(self, validated_data):
        user = self.context['request'].user
        album, _ = Album.objects.get_or_create(
            user=user,
            uri=validated_data['uri'],
            defaults={
                'title': validated_data['title'],
                'release_year': validated_data['release_year'],
                'cover_art': validated_data['cover_art'],
                'artist': validated_data['artist'],
            }
        )
        return album
    
# Serializer for the Collection Model
class CollectionSaveSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['artist', 'album'])
    selected_collections = serializers.ListField(child=serializers.CharField())
    uri = serializers.CharField()
    
    # Artist-specific
    name = serializers.CharField(required=False)
    image = serializers.URLField(required=False, allow_blank=True)
    
    # Album-specific
    title = serializers.CharField(required=False)
    release_year = serializers.IntegerField(required=False)
    cover_art = serializers.URLField(required=False, allow_blank=True)
    artist_name = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('selected_collections'):
            raise serializers.ValidationError("No Collections Selected.")
        
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        type_ = validated_data['type']
        collections = validated_data['selected_collections']
        created_obj = None

        if type_ == 'artist':
            artist_data = {
                "uri": validated_data["uri"],
                "name": validated_data["name"],
                "image": validated_data["image"]
            }
            serializer = ArtistSerializer(data=artist_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            created_obj = serializer.save()

        elif type_ == 'album':
            album_data = {
                "uri": validated_data["uri"],
                "title": validated_data["title"],
                "release_year": validated_data["release_year"],
                "cover_art": validated_data["cover_art"],
                "artist": validated_data["artist_name"]
            }
            serializer = AlbumSerializer(data=album_data, context=self.context)
            serializer.is_valid(raise_exception=True)
            created_obj = serializer.save()

        # Save to collections
        saved_collection_names = []
        for code in collections:
            collection = get_object_or_404(Collection, code=code)
            getattr(collection, f"{type_}s").add(created_obj)
            saved_collection_names.append(collection.name)

        return {
            "object": created_obj,
            "saved_to": saved_collection_names,
        }
