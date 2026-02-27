from django.urls import path
from items.views import (
    ItemListView,
    ItemControlStockUpdateAPIView,
    ItemDetailListView,
    SectionListView,
    ItemControlStockErrorListView,
)

urlpatterns = [
    path('item/', ItemDetailListView.as_view(), name='item-detail-list'),    
    path('items/', ItemListView.as_view(), name='items-view'),
    path('items/stock-errors/', ItemControlStockErrorListView.as_view(), name='stock-error-list'),
    path('items/control-stock/<str:code>/', ItemControlStockUpdateAPIView.as_view(), name='update_item_control_stock'),
    path('items/sections/', SectionListView.as_view(), name='section-list'),
]
