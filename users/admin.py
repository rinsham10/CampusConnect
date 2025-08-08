# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Job, StudentApplication, Resume

class CustomUserAdmin(UserAdmin):
    # This will display the 'role' field in the admin user list
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'created_at', 'deadline')
    search_fields = ('title', 'company')

class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'applied_date', 'status')
    list_filter = ('status', 'job__company')

# Unregister the default CustomUser admin if it was registered simply before
# admin.site.unregister(CustomUser) 
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(Job, JobAdmin)
admin.site.register(StudentApplication, StudentApplicationAdmin)
admin.site.register(Resume)