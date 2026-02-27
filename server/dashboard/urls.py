from django.urls import path
from dashboard.views import (
    DashboardStatsView,
    NoSalesStatsView,
    OCAwaitingStatsView,
)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('stats/no-sales/', NoSalesStatsView.as_view(), name='no-sales-stats'),
    path('stats/oc-awaiting/', OCAwaitingStatsView.as_view(), name='oc-awaiting-stats'),
]
