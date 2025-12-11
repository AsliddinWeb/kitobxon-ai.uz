"""
Kitobxon AI - URL Configuration
"""

from django.contrib import admin
from django.urls import path, include

# Static
from django.conf import settings
from django.conf.urls.static import static

# Admin name
admin.site.site_title = "Admin"
admin.site.site_header = "Kitobxon AI"
admin.site.index_title = "Dashboard"

# Urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.books.urls', namespace='books')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('chat/', include('apps.ai_chat.urls', namespace='ai_chat')),
    path('summary/', include('apps.summarizer.urls', namespace='summarizer')),
    path('quiz/', include('apps.quiz.urls', namespace='quiz')),
    path('tracker/', include('apps.tracker.urls', namespace='tracker')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)