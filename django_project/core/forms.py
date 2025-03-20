from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User, Collection

# Custom user creation form extending Django's built-in UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "id": "password1",
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(
            attrs={
                "id": "password2",
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "Password Confirmation",
            }
        ),
    )

    class Meta:
        model = User  
        fields = [
            "username",
            "first_name",
            "password1",
            "password2",
            "private",
            "profile_picture",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "id": "username",
                    "class": "form-control",
                    "placeholder": "Username",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "id": "first_name",
                    "class": "form-control",
                    "placeholder": "First Name",
                }
            ),
            "private": forms.CheckboxInput(
                attrs={
                    "id": "private",
                    "class": "form-check-input",
                }
            ),
            "profile_picture": forms.FileInput(
                attrs={
                    "id": "profile_picture",
                    "class": "form-control-file",
                    "accept": "image/*",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensuring required fields are explicitly set
        self.fields["username"].required = True
        self.fields["first_name"].required = True
        self.fields["password1"].required = True
        self.fields["password2"].required = True


# Custom authentication form for user login
class AuthenticationForm(forms.Form):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "class": "form-control",
                "autocomplete": "username",
                "autofocus": True,
                "placeholder": "Username",
            }
        ),
    )

    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "id": "password",
                "class": "form-control",
                "autocomplete": "current-password",
                "placeholder": "Password",
            }
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request  # Store request for authentication
        self.user = None  # Placeholder for authenticated user

    def clean(self):
        """
        Authenticate user with provided credentials.
        """
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username is not None and password:
            self.user = authenticate(self.request, username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid login. Please enter the correct username and password.")
        return self.cleaned_data

    def get_user(self):
        """
        Returns the authenticated user instance.
        """
        return self.user


# Form for creating and managing collections
class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ["name", "description", "collection_type", "thumbnail"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "id": "name",
                    "class": "form-control",
                    "autofocus": True,
                    "placeholder": "Collection Name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "id": "description",
                    "class": "form-control",
                    "placeholder": "Description of your collection",
                }
            ),
            "collection_type": forms.Select(
                attrs={
                    "id": "collection_type",
                    "class": "form-control",
                }
            ),
            "thumbnail": forms.FileInput(
                attrs={
                    "id": "thumbnail",
                    "class": "form-control-file",
                    "accept": "image/*",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enforcing required fields
        self.fields["name"].required = True
        self.fields["collection_type"].required = True


# Form for updating user profile information
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User  # Using custom User model
        fields = ["username", "first_name", "profile_picture", "private", "profile_hue"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "id": "username",
                    "class": "form-control",
                    "placeholder": "Username",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "id": "first_name",
                    "class": "form-control",
                    "placeholder": "First Name",
                }
            ),
            "private": forms.CheckboxInput(
                attrs={
                    "id": "private",
                    "class": "form-check-input",
                }
            ),
            "profile_picture": forms.FileInput(
                attrs={
                    "id": "profile_picture",
                    "class": "form-control-file",
                    "accept": "image/*",
                }
            ),
            "profile_hue": forms.TextInput(
                attrs={
                    "id": "profile_hue",
                    "class": "form-control",
                    "type": "color",
                }
            ),
        }
