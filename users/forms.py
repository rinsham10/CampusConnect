from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, Resume
from django.contrib.auth.forms import AuthenticationForm

class RegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        label='Full Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter Full Name', 'id': 'full_name'})
    )
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': 'Enter Username', 'id': 'username'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email', 'id': 'email'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Create Password', 'id': 'password'}),
        required=True
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'id': 'confirm_password'}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

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


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Username', 'id': 'username'}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'id': 'password'}
    ))


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        labels = {
            'file': 'Select PDF File',
        }
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file and not file.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        return file
