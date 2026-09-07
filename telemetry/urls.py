from django.urls import path
from . import views

urlpatterns = [
    path('trips/start/', views.start_trip, name='start-trip'),
    path('trips/upload-summary/', views.upload_summary, name='upload-trip-summary'),
]