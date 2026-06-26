from django.contrib import admin

from .models import Habit, HabitLaw, HabitStack, HabitStackItem


class HabitLawInline(admin.StackedInline):
    model = HabitLaw
    can_delete = False


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'habit_type', 'identity', 'is_active', 'created_at')
    inlines = [HabitLawInline]


class HabitStackItemInline(admin.TabularInline):
    model = HabitStackItem
    extra = 0


@admin.register(HabitStack)
class HabitStackAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    inlines = [HabitStackItemInline]