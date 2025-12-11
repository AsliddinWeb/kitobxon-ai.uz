from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('update-progress/', views.update_progress, name='update_progress'),
    path('start-reading/<slug:book_slug>/', views.start_reading, name='start_reading'),
]