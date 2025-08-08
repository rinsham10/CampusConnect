# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.title} at {self.company}'

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