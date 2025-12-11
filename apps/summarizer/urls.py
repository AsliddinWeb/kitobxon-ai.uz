from django.urls import path
from . import views

app_name = 'summarizer'

urlpatterns = [
    path('<slug:book_slug>/', views.summary_view, name='summary'),
    path('generate/<slug:book_slug>/', views.generate_summary, name='generate'),
]