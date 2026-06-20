from django.urls import path

from .views import IdentityListCreateView, PresetIdentitiesView

urlpatterns = [
    path('presets/', PresetIdentitiesView.as_view(), name='identity-presets'),
    path('', IdentityListCreateView.as_view(), name='identity-list-create'),
]