from django.urls import path
from users.views import (
    UserListCreateView, 
    UserRetrieveUpdateDestroyView, 
    UserUpdateView,
    PasswordChangeView,
)

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/change-password/', PasswordChangeView.as_view(), name='user-change-password'),
]
