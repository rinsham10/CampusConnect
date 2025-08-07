# users/admin.py

from django.contrib import admin
from .models import CustomUser

# This line tells the admin site to manage the CustomUser model
admin.site.register(CustomUser)