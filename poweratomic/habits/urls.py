from django.urls import path

from .views import HabitDetailView, HabitListCreateView, HabitStackDetailView, HabitStackListCreateView

urlpatterns = [
    path('stacks/<uuid:pk>/', HabitStackDetailView.as_view(), name='habit-stack-detail'),
    path('stacks/', HabitStackListCreateView.as_view(), name='habit-stack-list-create'),
    path('<uuid:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('', HabitListCreateView.as_view(), name='habit-list-create'),
]