from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User, Collection

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "id": "password1",
            "class": "form-control",
            "autocomplete": "new-password",
            "placeholder": "Password"
        }),
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(attrs={
            "id": "password2",
            "class": "form-control",
            "autocomplete": "new-password",
            "placeholder": "Password Confirmation"
        }),
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
            "username": forms.TextInput(attrs={
                "id": "username",
                "class": "form-control",
                "placeholder": "Username"
            }),
            "first_name": forms.TextInput(attrs={
                "id": "first_name",
                "class": "form-control",
                "placeholder": "First Name"
            }),
            "private": forms.CheckboxInput(attrs={
                "id": "private",
                "class": "form-check-input",
            }),
            "profile_picture": forms.ClearableFileInput(attrs={
                "id": "profile_picture",
                "class": "form-control-file",
                "accept": "image/*",
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].required = True
        self.fields["first_name"].required = True
        self.fields["password1"].required = True
        self.fields["password2"].required = True
        
class AuthenticationForm(forms.Form):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "class": "form-control",
                "autocomplete": "username",
                "autfocus": True,
                "placeholder": "Username"
            }
        )
    )
    
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "id": "password",
                "class": "form-control",
                "autocomplete": "current-password",
                "autofocus": False,
                "placeholder": "Password",
            }
        ),
    )
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username is not None and password:
            self.user = authenticate(self.request, username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid login. Please enter the correct username and password.")
        return self.cleaned_data

    def get_user(self):
        return self.user
    
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
            "thumbnail": forms.ClearableFileInput(
                attrs={
                    "id": "thumbnail",
                    "class": "form-control-file",
                    "accept": "image/*",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["collection_type"].required = True

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'profile_picture', 'private', 'profile_hue'] 
        widgets = {
            "username": forms.TextInput(attrs={
                "id": "username",
                "class": "form-control",
                "placeholder": "Username"
            }),
            "first_name": forms.TextInput(attrs={
                "id": "first_name",
                "class": "form-control",
                "placeholder": "First Name"
            }),
            "private": forms.CheckboxInput(attrs={
                "id": "private",
                "class": "form-check-input",
            }),
            "profile_picture": forms.FileInput(attrs={
                "id": "profile_picture",
                "class": "form-control-file",
                "accept": "image/*",
            }),
            "profile_hue": forms.TextInput(attrs={
                "id": "profile_hue",
                "class": "form-control",
                "type": "color"
            })
        }

    # Optional: You can add custom validation for the username field to check if it's already taken
    def clean(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

