from django.urls import path
from . import views

app_name = 'ai_chat'

urlpatterns = [
    path('<slug:book_slug>/', views.chat_view, name='chat'),
    path('api/send/', views.send_message, name='send_message'),
    path('clear/<int:session_id>/', views.clear_chat, name='clear_chat'),
    path('history/', views.chat_history, name='history'),
]