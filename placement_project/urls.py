# placement_project/urls.py

from django.contrib import admin
# This line is ESSENTIAL. It makes path() and include() available.
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # This now correctly uses the URL NAME 'login', not the path.
    # Django will find its full path at '/accounts/login/'.
    path('', lambda request: redirect('login', permanent=False)),

    # Include your other app URLs
    path('predictor/', include('predictor.urls')),
    path('accounts/', include('users.urls')),
]