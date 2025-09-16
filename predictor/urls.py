from django.urls import path
from . import views

urlpatterns = [
    # The main URL '' now points to your NEW, renamed predict_view.
    path('', views.predict_view, name='predict'),

    # The OLD predictor is now accessible at this backup URL, but hidden from regular users.
    path('v1/', views.predict_old_view, name='predict_old'),
]