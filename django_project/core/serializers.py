from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'private', 'profile_picture', 'profile_hue']
        
    def update(self, instance, validated_data):
        
        # If no new profile picture, keep the old one
        if validated_data["profile_picture"] is None:
            validated_data["profile_picture"] = instance.profile_picture
        
        # Check if the username is changing and if it's already taken
        new_username = validated_data.get("username", instance.username)
        if new_username != instance.username and User.objects.filter(username=new_username).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        
        # Revert the privacy if user checked the box in frontend
        if validated_data["private"] == True:
           validated_data["private"] = not instance.private

        return super().update(instance, validated_data)