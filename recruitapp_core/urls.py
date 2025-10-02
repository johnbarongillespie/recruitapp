from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line correctly includes all URLs from your 'recruiting' app
    path('', include('recruiting.urls')),
]