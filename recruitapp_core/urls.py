from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Path for the Django Admin site
    path('admin/', admin.site.urls),

    # This one line now handles ALL other paths, passing them to our app
    path('', include('recruiting.urls')),
]