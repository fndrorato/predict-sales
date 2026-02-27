from django.urls import path
from notifications.views import MyNotificationsView

urlpatterns = [
    path("notifications/", MyNotificationsView.as_view(), name="my-notifications"),
]
