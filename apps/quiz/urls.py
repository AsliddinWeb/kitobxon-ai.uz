from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('start/<slug:book_slug>/', views.quiz_start, name='start'),
    path('generate/<slug:book_slug>/', views.generate_quiz, name='generate'),
    path('take/<int:quiz_id>/', views.take_quiz, name='take'),
    path('result/<int:attempt_id>/', views.quiz_result, name='result'),
]
