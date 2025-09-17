from django.urls import path
from . import views

urlpatterns = [
    # The main page, served by the 'index' view
    path('', views.index, name='index'),

    # The path for our AI queries, served by the 'ask_agent' view
    path('ask/', views.ask_agent, name='ask_agent'),

    # The path for the session history API
    path('sessions/', views.get_chat_sessions, name='get_chat_sessions'),
]