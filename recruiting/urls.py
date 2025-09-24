from django.urls import path, include
from . import views

urlpatterns = [
    # The root path now serves our landing page
    path('', views.landing_page, name='landing_page'),
    
    # The path for our main agent/chat interface
    path('agent/', views.index, name='index'),

    # The path for our AI's API endpoint
    path('agent/ask/', views.ask_agent, name='ask_agent'),
    
    # The path for the session history API (from your existing file)
    path('sessions/', views.get_chat_sessions, name='get_chat_sessions'),

    # This single line includes all of allauth's URLs (login, logout, signup, etc.)
    path('accounts/', include('allauth.urls')),
]