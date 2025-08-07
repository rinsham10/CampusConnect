# users/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class RegistrationForm(forms.ModelForm):
    # We define all fields here to control their widgets and labels
    full_name = forms.CharField(
        label='Full Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Full Name',
            'id': 'full_name' # ID for JavaScript
        })
    )
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Username',
            'id': 'username' # ID for JavaScript
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter Email',
            'id': 'email' # ID for JavaScript
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create Password',
            'id': 'password' # ID for JavaScript
        }),
        required=True
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'id': 'confirm_password' # ID for JavaScript
        }),
        required=True
    )

    class Meta:
        model = CustomUser
        # The fields Django will save to the model
        fields = ['username', 'email']

    # Your validation methods (clean_username, clean_email, clean) remain the same.
    # They are crucial for secure, backend validation.
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

# ... your LoginForm remains here ...

class LoginForm(forms.Form):
    # We add widgets to control the HTML attributes
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Username',
            'id': 'username', # Match the ID from your example JS
        }
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'placeholder': 'Password',
            'id': 'password', # Match the ID from your example JS
        }
    ))