# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Split 'full_name' into first_name and last_name
            full_name = form.cleaned_data.get('full_name').split()
            user.first_name = full_name[0]
            if len(full_name) > 1:
                user.last_name = ' '.join(full_name[1:])
            # Set and hash the password
            user.set_password(form.cleaned_data.get('password'))
            # All users registered through this form are students
            user.role = 'STUDENT'
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Role-based redirection logic
                if user.role == 'ADMIN':
                    return redirect('admin:index')  # Django's built-in admin dashboard
                else:
                    return redirect('dashboard') # Student dashboard
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def student_dashboard_view(request):
    # This page is for students. A decorator could protect it further.
    return render(request, 'users/student_dashboard.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')