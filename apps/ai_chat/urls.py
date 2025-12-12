from django.urls import path
from . import views

app_name = 'ai_chat'

urlpatterns = [
    # Taqqoslash URL'lari
    path('compare/', views.compare_view, name='compare'),
    path('comparison/<uuid:comparison_id>/', views.comparison_detail_view, name='comparison_detail'),
    path('my-comparisons/', views.my_comparisons_view, name='my_comparisons'),
    path('comparison/<uuid:comparison_id>/delete/', views.delete_comparison_view, name='delete_comparison'),

    # Chat URL'lari
    path('<slug:book_slug>/', views.chat_view, name='chat'),
    path('api/send/', views.send_message, name='send_message'),
    path('clear/<int:session_id>/', views.clear_chat, name='clear_chat'),
    path('history/', views.chat_history, name='history'),
]
