from django.urls import path

from . import views

urlpatterns = [
    path('settings/', views.PomodoroSettingsView.as_view(), name='pomodoro-settings'),
    path('sessions/', views.PomodoroSessionListCreateView.as_view(), name='pomodoro-session-list'),
    path('sessions/<uuid:pk>/complete/', views.PomodoroSessionCompleteView.as_view(), name='pomodoro-session-complete'),
    path('sessions/<uuid:pk>/abandon/', views.PomodoroSessionAbandonView.as_view(), name='pomodoro-session-abandon'),
    path('stats/', views.PomodoroStatsView.as_view(), name='pomodoro-stats'),
]