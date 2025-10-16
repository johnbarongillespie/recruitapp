# recruitapp_core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # This line correctly includes all URLs from your 'recruiting' app
    path('', include('recruiting.urls')),
]

# Serve static files in development using Django's staticfiles app
# This properly serves files from STATICFILES_DIRS during development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()