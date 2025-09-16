from django.urls import path
from . import views  # Ensure 'views' is imported

urlpatterns = [
    # This is your ORIGINAL predictor. It remains unchanged.
    path('', views.predict_view, name='predict'),

    # This is the NEW path for your enhanced predictor.
    # It will be accessible at a URL like "yourdomain.com/predictor/new"
    path('new/', views.predict_v2_view, name='predict_v2'),
]