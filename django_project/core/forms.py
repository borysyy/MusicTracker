from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name" ,"password1", "password2"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["username"].required = True
        self.fields["first_name"].required = True
        self.fields["password1"].required = True
        self.fields["password2"].required = True
        
        self.fields["username"].widget.attrs.update(
            {
                "id": "username",
                "class": "form-control",
                "autofocus": True,
                "placeholder": 'Username'
            }
        )
        
        self.fields["first_name"].widget.attrs.update(
            {
                "id": "first_name",
                "class": "form-control",
                "autofocus": False,
                "placeholder": 'First Name'
            }
        )
        
        self.fields["password1"].widget.attrs.update(
            {
                "id": "password1",
                "class": "form-control",
                "autocomplete": "new-password",
                "autofocus": False,
                "placeholder": "Password"
            }
        )
        
        self.fields["password2"].widget.attrs.update(
            {
                "id": "password2",
                "class": "form-control",
                "autocomplete": "new-password",
                "autofocus": False,
                "placeholder": "Password Confirmation"
            }
        )