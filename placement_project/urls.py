from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static  # 👈 this is needed

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login', permanent=False)),
    path('predictor/', include('predictor.urls')),
    path('accounts/', include('users.urls')),
]

# ✅ Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
