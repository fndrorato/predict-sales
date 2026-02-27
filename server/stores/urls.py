from django.urls import path
from stores.views import StoreListView


urlpatterns = [
    path('stores/', StoreListView.as_view(), name='store-list'),
]
