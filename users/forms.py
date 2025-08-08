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


class ApplicationForm(forms.Form):
    # Field for selecting an existing resume. We'll populate this in the view.
    existing_resume = forms.ModelChoiceField(
        queryset=None, 
        widget=forms.RadioSelect, 
        required=False,
        empty_label=None, # Removes the "---------" option
        label="Choose from your saved resumes"
    )

    # Field for uploading a new resume
    new_resume = forms.FileField(
        required=False, 
        label="Or upload a new resume (PDF only)"
    )

    def __init__(self, *args, **kwargs):
        # We need the user to filter the queryset of existing resumes
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # The queryset for the field is set here, filtered for the current user
            self.fields['existing_resume'].queryset = Resume.objects.filter(student=user)

    # This is the magic part: custom validation logic
    def clean(self):
        cleaned_data = super().clean()
        existing_resume = cleaned_data.get('existing_resume')
        new_resume = cleaned_data.get('new_resume')

        if not existing_resume and not new_resume:
            raise forms.ValidationError("You must either select an existing resume or upload a new one.")

        if existing_resume and new_resume:
            raise forms.ValidationError("Please either select an existing resume or upload a new one, not both.")
        
        # Validate that the new resume is a PDF
        if new_resume and not new_resume.name.endswith('.pdf'):
            self.add_error('new_resume', "Only PDF files are allowed.")
            
        return cleaned_data