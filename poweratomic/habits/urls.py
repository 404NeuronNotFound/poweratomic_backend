from django.urls import path

from .views import (
    HabitDetailView,
    HabitListCreateView,
    HabitStackDetailView,
    HabitStackListCreateView,
    StackCompleteView,
)

urlpatterns = [
    # Must come before stacks/<uuid:pk>/ - otherwise Django tries to
    # parse "complete" as the <uuid:pk> segment and 404s before this
    # pattern is ever reached.
    path('stacks/<uuid:pk>/complete/', StackCompleteView.as_view(), name='habit-stack-complete'),
    path('stacks/<uuid:pk>/', HabitStackDetailView.as_view(), name='habit-stack-detail'),
    path('stacks/', HabitStackListCreateView.as_view(), name='habit-stack-list-create'),
    path('<uuid:pk>/', HabitDetailView.as_view(), name='habit-detail'),
    path('', HabitListCreateView.as_view(), name='habit-list-create'),
]