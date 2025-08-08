# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

# --- Your Existing CustomUser Model (Unchanged) ---
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)

# --- NEW MODELS FOR THE DASHBOARD ---

# 1. Profile Model
# This will store extra information about a student, like their profile completion.
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    profile_completion = models.IntegerField(default=20) # Start at 20% for a new account

    def __str__(self):
        return f'{self.user.username} Profile'

# Use signals to automatically create a Profile whenever a new CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'STUDENT':
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

# 2. Job Model
# This will be created by the Admin in the Django Admin Panel.
class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "Full-time", "Full-time"
        PART_TIME = "Part-time", "Part-time"
        INTERNSHIP = "Internship", "Internship"
        CONTRACT = "Contract", "Contract"

    # Core Info
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, default="Work From Home (Remote)")
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    
    # Detailed Description Fields
    description = models.TextField(blank=True, null=True, help_text="A general overview of the job and company.")
    key_responsibilities = models.TextField(blank=True, null=True, help_text="List the primary duties and responsibilities.")
    minimum_qualifications = models.TextField(blank=True, null=True, help_text="List the essential qualifications and skills.")
    
    # Skills - stored as comma-separated values
    required_skills = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated list of skills (e.g., Python, Django, SQL)")
    
    # Sidebar Info
    recommendation = models.TextField(blank=True, null=True, help_text="A short recommendation or highlight for the job.")
    cgpa_requirement = models.CharField(max_length=50, blank=True, null=True, default="Not specified")
    
    # Salary & Dates
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default="INR")
    joining_date = models.DateField(blank=True, null=True)
    application_opens = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True) # This is the Application Deadline
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} at {self.company}'

    # A helper method to get skills as a list
    def get_skills_as_list(self):
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',')]
        return []
    

# 3. Student Application Model
# This links a student (CustomUser) to a Job they have applied for.
class StudentApplication(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Rejected', 'Rejected'),
        ('Accepted', 'Accepted'),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')

    def __str__(self):
        return f'{self.student.username} applied for {self.job.title}'

# 4. Resume Model
# To store student resumes.
class Resume(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Resume for {self.student.username}'

    # ADD THIS HELPER METHOD
    @property
    def filename(self):
        return os.path.basename(self.file.name)