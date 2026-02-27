from django.urls import path
from companies.views import (
    CompanyDetailView, 
    CompanySettingsListCreateView, 
    CompanySettingsDetailView,
    GroupListView,
)

urlpatterns = [
    path('company/groups/', GroupListView.as_view(), name='groups-list'),
    path('company/settings/', CompanySettingsListCreateView.as_view(), name='company-settings-list-create'),
    path('company/settings/<int:company_id>/', CompanySettingsDetailView.as_view(), name='company-settings-detail'),        
    path('company/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
]
