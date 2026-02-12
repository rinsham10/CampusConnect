from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from users import api_views  # 👈 this is needed

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login', permanent=False)),
    path('predictor/', include('predictor.urls')),
    path('accounts/', include('users.urls')),
    path('api/register/', api_views.RegisterAPI.as_view(), name='api_register'),
    path('api/login/', api_views.LoginAPI.as_view(), name='api_login'),
    path('api/predict/', api_views.PredictAPI.as_view(), name='api_predict'),
    path('api/jobs/', api_views.JobListAPI.as_view(), name='api_job_list'),
    path('api/jobs/apply/', api_views.ApplyJobAPI.as_view(), name='api_apply'),
    path('api/jobs/<int:pk>/', api_views.JobDetailAPI.as_view(), name='api_job_detail'),
]

# ✅ Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
