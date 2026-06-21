from django.contrib import admin

from .models import Habit, HabitLaw


class HabitLawInline(admin.StackedInline):
    model = HabitLaw
    can_delete = False


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'habit_type', 'identity', 'is_active', 'created_at')
    inlines = [HabitLawInline]