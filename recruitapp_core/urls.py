from django.contrib import admin
from django.urls import path, include
from recruiting import views as recruiting_views # <-- UPDATED IMPORT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recruiting.urls')), # <-- UPDATED PATH
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', recruiting_views.register, name='register'), # <-- UPDATED VIEW
    # Add this new path for handling the verification link
    path('verify/<str:uidb64>/<str:token>/', recruiting_views.verify_email, name='verify_email'), # <-- UPDATED VIEW
]