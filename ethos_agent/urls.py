from django.urls import path
from . import views

urlpatterns = [
    # The main page, served by the 'index' view
    path('', views.index, name='index'),
    # The new path for our AI queries, served by the 'ask_agent' view
    path('ask/', views.ask_agent, name='ask_agent'),
]