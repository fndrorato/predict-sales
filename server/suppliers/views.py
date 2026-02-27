from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from orders.models import OrderSystemResult
from stores.models import Store
from suppliers.models import Supplier
from suppliers.serializers import (
    SupplierStoreInputSerializer,
    SupplierOCResultSerializer,
    SupplierSerializer
)


class SupplierOCStatusAPIView(GenericAPIView):
    serializer_class = SupplierStoreInputSerializer

    @extend_schema(
        request=SupplierStoreInputSerializer,
        responses=SupplierOCResultSerializer,
        tags=["suppliers"],
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supplier_code = serializer.validated_data['supplier_code']
        store_code = serializer.validated_data['store_code']

        try:
            supplier = Supplier.objects.get(code=supplier_code)
        except Supplier.DoesNotExist:
            return Response({'error': 'Fornecedor não encontrado.'}, status=404)

        try:
            store = Store.objects.get(code=store_code)
        except Store.DoesNotExist:
            return Response({'error': 'Loja não encontrada.'}, status=404)

        ocs = OrderSystemResult.objects.filter(
            supplier=supplier,
            store=store
        ).order_by('-date')[:3]

        open_ocs = [oc.oc_number for oc in ocs if oc.is_open]

        return Response({
            'supplier_name': supplier.name,
            'oc_numbers_pending': open_ocs
        }, status=200)

@extend_schema(
    summary="Buscar fornecedor(s)",
    description="Busca um fornecedor pelo código exato ou vários pelo nome (contendo a palavra).",
    parameters=[
        OpenApiParameter(name='code', description='Código exato do fornecedor', required=False, type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='query', description='Busca por nome (ex: NISSIN)', required=False, type=str, location=OpenApiParameter.QUERY),
    ],
    tags=['suppliers'],
    responses=SupplierSerializer(many=True)
)
class SupplierListView(ListAPIView):
    serializer_class = SupplierSerializer

    def get_queryset(self):
        code = self.request.query_params.get('code')
        query = self.request.query_params.get('query')

        if code:
            return Supplier.objects.filter(code=code)

        if query:
            return Supplier.objects.filter(name__icontains=query)

        raise ValidationError({'error': 'Informe ao menos um parâmetro: "code" ou "query".'})
