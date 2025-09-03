from django.contrib import admin
from django.urls import path, include
from ethos_agent import views as agent_views # Import our app's views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('agent/', include('ethos_agent.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # Add this new path for our custom registration page
    path('accounts/register/', agent_views.register, name='register'),
]