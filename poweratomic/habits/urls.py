from django.urls import path

from .views import HabitDetailView, HabitListCreateView

urlpatterns = [
    path('<uuid:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('', HabitListCreateView.as_view(), name='habit-list-create'),
]