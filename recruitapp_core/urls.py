from django.contrib import admin
from django.urls import path, include
from recruitapp_core import views as agent_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('agent/', include('recruiting.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', agent_views.register, name='register'),
    # Add this new path for handling the verification link
    path('verify/<str:uidb64>/<str:token>/', agent_views.verify_email, name='verify_email'),
]