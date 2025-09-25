# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Job, StudentApplication, Resume

# --- 1. NEW: Define the custom admin "action" for approval ---
@admin.action(description='Activate selected user accounts')
def make_active(modeladmin, request, queryset):
    """
    This action sets the 'is_active' flag to True for all selected users.
    """
    queryset.update(is_active=True)
# --- End of new section ---


class CustomUserAdmin(UserAdmin):
    # This will display the 'role' field in the admin user list
    # MODIFIED: Added 'is_active' to the list_display to see pending users
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'is_active')

    # ADDED: A filter to easily find inactive users awaiting approval
    list_filter = UserAdmin.list_filter + ('is_active', 'role')

    # ADDED: The new approval action to the actions dropdown
    actions = [make_active]
    
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

# Your registrations remain the same, but the CustomUser is now enhanced.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(Job, JobAdmin)
admin.site.register(StudentApplication, StudentApplicationAdmin)
admin.site.register(Resume)