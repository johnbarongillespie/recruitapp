from django.contrib import admin
from django.urls import path, include
from recruiting import views as recruiting_views

urlpatterns = [
    # Path for the Django Admin site
    path('admin/', admin.site.urls),

    # Paths for Django's built-in authentication (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Paths for our custom registration and email verification views
    path('accounts/register/', recruiting_views.register, name='register'),
    path('verify/<str:uidb64>/<str:token>/', recruiting_views.verify_email, name='verify_email'),

    # Includes all URLs from our main 'recruiting' app (homepage, chat API, etc.)
    path('', include('recruiting.urls')),
]