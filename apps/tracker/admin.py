from django.contrib import admin
from .models import ReadingSession, Achievement, UserAchievement, DailyStreak


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'current_page', 'pages_read', 'progress_percentage', 'completed', 'started_at']
    list_filter = ['completed', 'started_at']
    search_fields = ['user__username', 'book__title']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'condition_type', 'condition_value', 'points']
    list_filter = ['condition_type']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['earned_at']
    search_fields = ['user__username']


@admin.register(DailyStreak)
class DailyStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'pages_read']
    list_filter = ['date']
    search_fields = ['user__username']