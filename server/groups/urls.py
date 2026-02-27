from django.urls import path
from .views import GroupListCreateView, GroupDetailView, PermissionListView

urlpatterns = [
    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
]
