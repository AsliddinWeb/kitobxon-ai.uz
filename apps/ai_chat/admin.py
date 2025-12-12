from django.contrib import admin
from .models import ChatSession, Message, BookComparison, Recommendation


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['role', 'content', 'created_at']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'book__title']
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'short_content', 'created_at']
    list_filter = ['role', 'created_at']

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Xabar'


@admin.register(BookComparison)
class BookComparisonAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'book1', 'book2', 'views_count', 'created_at']
    list_filter = ['created_at', 'views_count']
    search_fields = ['user__username', 'book1__title', 'book2__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['id', 'created_at', 'updated_at', 'views_count']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'short_request', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'request_text']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

    def short_request(self, obj):
        return obj.request_text[:50] + '...' if len(obj.request_text) > 50 else obj.request_text
    short_request.short_description = 'So\'rov'