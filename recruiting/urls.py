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
    
    # --- START NEW URLS FOR SPRINT 1 ---
    
    # Ledger Routes (Milestone 2)
    path('ledger/', views.ledger_list, name='ledger_list'),
    path('ledger/save/', views.save_to_ledger, name='save_to_ledger'),
    path('ledger/<int:entry_id>/delete/', views.delete_ledger_entry, name='delete_ledger_entry'),
    
    # Action Item Routes (Milestone 3)
    path('action-items/', views.action_items_list, name='action_items_list'),
    path('action-items/generate/', views.generate_action_items, name='generate_action_items'),
    path('action-items/<int:item_id>/toggle/', views.toggle_action_item_complete, name='toggle_action_item_complete'),

    # --- END NEW URLS ---

    # ADMIN ROUTES (Milestone 3)
    path('admin/toggle-untethered/', views.toggle_untethered_mode, name='toggle_untethered_mode'),

    # DEVELOPMENT/TESTING ONLY (REMOVE BEFORE PRODUCTION)
    path('dev/reset-my-data/', views.reset_my_data, name='reset_my_data'),

    # FAMILY ACCOUNT SETUP (Milestone 4)
    path('setup/role/', views.role_selection, name='role_selection'),

    path('accounts/', include('allauth.urls')),
]