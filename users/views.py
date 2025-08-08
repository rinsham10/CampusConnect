# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from .models import StudentApplication, Job, Resume, Profile
from django.utils import timezone
from datetime import timedelta

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

@login_required
def student_dashboard_view(request):
    # Ensure this view is only for students
    if request.user.role != 'STUDENT':
        return redirect('admin:index') # Or some other appropriate page

    student = request.user
    
    # --- Fetch all the dynamic data for the dashboard ---
    
    # 1. Total Applications by this student
    total_applications = StudentApplication.objects.filter(student=student).count()
    
    # 2. Profile Completion (from the related Profile model)
    # get_or_create is robust, handling cases where a profile might not exist for an old user
    profile, created = Profile.objects.get_or_create(user=student)
    profile_completion = profile.profile_completion
    
    # 3. Deadlines (count of jobs with deadlines in the next 7 days)
    one_week_from_now = timezone.now().date() + timedelta(days=7)
    upcoming_deadlines_count = Job.objects.filter(
        deadline__gte=timezone.now().date(), 
        deadline__lte=one_week_from_now
    ).count()
    
    # 4. Total Resumes uploaded by the student
    total_resumes = Resume.objects.filter(student=student).count()

    # 5. Get the 2 most recent applications
    recent_applications_list = StudentApplication.objects.filter(student=student).order_by('-applied_date')[:2]

    context = {
        'user': student,
        'total_applications': total_applications,
        'profile_completion': profile_completion,
        'deadlines': upcoming_deadlines_count,
        'recent_resumes': total_resumes,
        'recent_applications_list': recent_applications_list,
        'last_updated': timezone.now()
    }
    return render(request, 'users/student_dashboard.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

