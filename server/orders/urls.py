from django.urls import path
from orders.views import (
    OrderStartDefaultView,
    OrderSystemGroupedListView,
    OrderDetailStockListAPIView,
    OrderListCreateAPIView,
    OrderRetrieveUpdateDestroyAPIView,
    OrderPendingListView,
    OrderBulkUpdateStatusView,
    OrderExportExcelView,
    OrderLogListView,
)

urlpatterns = [
    path('orders/list-pending', OrderPendingListView.as_view(), name='orders-list-pending-approval'),
    path('orders/update-status/', OrderBulkUpdateStatusView.as_view(), name='order-update-status'),
    
    path('orders/logs/<int:order_id>/', OrderLogListView.as_view(), name='order-log-list'),
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/export-excel/', OrderExportExcelView.as_view(), name='order-export-excel'),
    path('orders/<int:pk>/', OrderRetrieveUpdateDestroyAPIView.as_view(), name='order-detail'), 

    path('order-default/', OrderStartDefaultView.as_view(), name='order-start-default'),
    path('order-system/<int:oc_number>/', OrderSystemGroupedListView.as_view(), name='order-detail-system'),
    path('order-default-detail/', OrderDetailStockListAPIView.as_view(), name='order-start-default-detail-list'),
    
]
