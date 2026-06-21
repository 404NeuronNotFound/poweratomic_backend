from django.urls import path

from .views import HabitListCreateView

urlpatterns = [
    path('', HabitListCreateView.as_view(), name='habit-list-create'),
]