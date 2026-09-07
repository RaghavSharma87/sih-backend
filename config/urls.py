from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/v1/maps/', include('maps.urls')),
    path('api/v1/telemetry/', include('telemetry.urls')), # Add this line
]