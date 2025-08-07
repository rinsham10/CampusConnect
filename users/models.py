# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"

    # We don't need a `full_name` field here, Django's User model
    # already has `first_name` and `last_name`. We'll handle this in the form.
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)