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
    list_display = ('title', 'company', 'job_type', 'location', 'deadline')
    search_fields = ('title', 'company', 'description')
    list_filter = ('job_type', 'location')
    
    fieldsets = (
        ("Core Information", {
            'fields': ('title', 'company', 'job_type', 'location')
        }),
        ("Job Descriptions", {
            'fields': ('description', 'key_responsibilities', 'minimum_qualifications', 'required_skills')
        }),
        ("Sidebar Information", {
            'fields': ('recommendation', 'cgpa_requirement')
        }),
        ("Salary & Dates", {
            'fields': ('currency', 'salary_min', 'salary_max', 'joining_date', 'application_opens', 'deadline')
        }),
    )



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