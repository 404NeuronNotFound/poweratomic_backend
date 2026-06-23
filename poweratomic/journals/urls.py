from django.urls import path

from .views import JournalHistoryView, JournalWriteView, TodayJournalView

urlpatterns = [
    path('today/', TodayJournalView.as_view(), name='journal-today'),
    path('history/', JournalHistoryView.as_view(), name='journal-history'),
    path('', JournalWriteView.as_view(), name='journal-write'),
]