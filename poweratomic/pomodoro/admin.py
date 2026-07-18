from django.contrib import admin

from .models import PomodoroSession, PomodoroSettings


@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'phase', 'status', 'habit', 'cycle_number', 'started_at', 'completed_at']
    list_filter = ['phase', 'status']
    search_fields = ['user__username', 'user__email']


@admin.register(PomodoroSettings)
class PomodoroSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'work_minutes', 'short_break_minutes', 'long_break_minutes', 'cycles_before_long_break']