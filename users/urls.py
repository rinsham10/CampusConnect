# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.student_dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('jobs/', views.job_list_view, name='job-list'),
    path('jobs/<int:job_id>/', views.job_detail_view, name='job-detail'),
    path('my-applications/', views.my_applications_view, name='my-applications'),
]