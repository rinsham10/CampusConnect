# users/views.py

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from .models import StudentApplication, Job, Resume, Profile
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

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

@login_required
def job_list_view(request):
    """This view displays all available jobs and handles search/filter functionality."""
    
    # Start with all jobs
    queryset = Job.objects.all().order_by('-created_at')
    
    # Get the filter parameters from the URL
    search_query = request.GET.get('q', '')
    location_filter = request.GET.get('location', '')
    job_type_filter = request.GET.get('type', '')
    
    # --- Apply filters if they exist ---
    
    # 1. Search filter (for title, company, or description)
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # 2. Location filter
    if location_filter:
        queryset = queryset.filter(location__iexact=location_filter)
        
    # 3. Job Type filter
    if job_type_filter:
        queryset = queryset.filter(job_type__iexact=job_type_filter)
        
    # --- Prepare data for dropdowns ---
    
    # Get distinct locations and job types from the database to populate the filters
    distinct_locations = Job.objects.values_list('location', flat=True).distinct().order_by('location')
    
    context = {
        'jobs': queryset,
        'job_types': Job.JobType.choices, # Pass the choices from the model
        'distinct_locations': distinct_locations,
        
        # Pass the current filter values back to the template to pre-fill the form
        'search_query': search_query,
        'location_filter': location_filter,
        'job_type_filter': job_type_filter,
    }
    return render(request, 'users/job_list.html', context)


@login_required
def job_detail_view(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    has_applied = StudentApplication.objects.filter(student=request.user, job=job).exists()

    if request.method == 'POST':
        if not has_applied:
            StudentApplication.objects.create(student=request.user, job=job)
            messages.success(request, f"You have successfully applied for the {job.title} position.")
            return redirect('job-detail', job_id=job.id)
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'skills_list': job.get_skills_as_list() # Pass the skill list to the template
    }
    return render(request, 'users/job_detail.html', context)


# users/views.py

@login_required
def my_applications_view(request):
    """This view lists all applications for the current student and handles search."""
    queryset = StudentApplication.objects.filter(student=request.user).order_by('-applied_date')
    search_query = request.GET.get('q', '')
    
    if search_query:
        # THE FIX IS HERE: We now search by the simple, built-in 'id' field
        queryset = queryset.filter(
            Q(job__title__icontains=search_query) |
            Q(job__company__icontains=search_query) |
            Q(id__icontains=search_query) 
        )
        
    total_applications = queryset.count()
    context = {
        'applications': queryset,
        'total_applications': total_applications,
        'search_query': search_query,
    }
    return render(request, 'users/my_applications.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

