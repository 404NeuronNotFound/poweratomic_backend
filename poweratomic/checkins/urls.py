from django.urls import path

from .views import CheckInCreateView, CheckInDeleteView, TodayCheckInsView

urlpatterns = [
    path('today/', TodayCheckInsView.as_view(), name='checkin-today'),
    path('<uuid:pk>/', CheckInDeleteView.as_view(), name='checkin-delete'),
    path('', CheckInCreateView.as_view(), name='checkin-create'),
]