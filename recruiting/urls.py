from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    
    # MODIFIED: These two paths now handle the main agent view and resuming a specific chat
    path('agent/', views.index, name='index'),
    path('agent/<uuid:session_id>/', views.index, name='view_session'),

    path('agent/ask/', views.ask_agent, name='ask_agent'),
    path('agent/task_status/<str:task_id>/', views.get_task_status, name='get_task_status'),
    path('sessions/', views.get_chat_sessions, name='get_chat_sessions'),
    path('agent/session/<uuid:session_id>/delete/', views.delete_session, name='delete_session'),
    path('agent/session/<uuid:session_id>/history/', views.get_session_history, name='get_session_history'),
    path('accounts/', include('allauth.urls')),
]