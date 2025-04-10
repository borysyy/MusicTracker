from rest_framework import serializers
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
