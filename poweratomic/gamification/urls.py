from django.urls import path

from .views import BadgeListView, ProgressView

urlpatterns = [
    path('badges/', BadgeListView.as_view(), name='badges'),
    path('', ProgressView.as_view(), name='progress'),
]