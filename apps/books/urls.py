from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('books/', views.book_list_view, name='list'),
    path('book/<slug:slug>/', views.book_detail_view, name='detail'),
    path('categories/', views.category_list_view, name='categories'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('author/<slug:slug>/', views.author_detail_view, name='author_detail'),
]