
from django.urls import path
from .views import SupplierOCStatusAPIView, SupplierListView

urlpatterns = [
    path('suppliers/', SupplierListView.as_view(), name='supplier-list-view'),
    path('supplier-info/', SupplierOCStatusAPIView.as_view(), name='supplier-oc-status'),
]
