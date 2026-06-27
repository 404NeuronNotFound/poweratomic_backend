from django.urls import path

from .views import CheckInCreateView, CheckInDeleteView, DashboardView, TodayCheckInsView

urlpatterns = [
    path('today/', TodayCheckInsView.as_view(), name='checkin-today'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('<uuid:pk>/', CheckInDeleteView.as_view(), name='checkin-delete'),
    path('', CheckInCreateView.as_view(), name='checkin-create'),
]