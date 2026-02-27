from app.permissions import GlobalDefaultPermission, CustomOrderPermission
from datetime import date
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, UpdateAPIView, ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from openpyxl import Workbook
from items.models import Item, ItemControlStock, Section
from orders.models import OrderSystem, Order, OrderStatus, OrderLog
from stores.models import Store
from stores.serializers import StoreSerializer
from items.models import Section, Subsection
from items.serializers import SectionSerializer
from notifications.models import Notification
from orders.serializers import (
    OrderStartDefaultSerializer, 
    OrderSystemItemSerializer, 
    OrderSystemGroupedSerializer,
    OrderDetailStockSerializer,
    OrderSerializer,
    OrderPendingSerializer,
    OrderBulkUpdateStatusSerializer,
    OrderLogSerializer,
)   
from utils.predictions import sales_forecast


@extend_schema(
    responses=OrderStartDefaultSerializer,
    summary="Lista todas as lojas e seções combinadas",
    description="Retorna um JSON com duas listas: `stores` e `sections`.",
    tags=["orders"]
)
class OrderStartDefaultView(ListAPIView):
    """
    Retorna a junção de stores e sections em um único JSON
    """
    def list(self, request, *args, **kwargs):
        stores = Store.objects.all()
        sections = Section.objects.all()

        stores_serialized = StoreSerializer(stores, many=True).data
        sections_serialized = SectionSerializer(sections, many=True).data

        return Response({
            'stores': stores_serialized,
            'sections': sections_serialized
        })

@extend_schema(
    responses=OrderSystemGroupedSerializer,
    summary="Lista informações de uma ordem de compra",
    description="Retorna um JSON com todas as informações de uma ordem de compra.",
    tags=["orders"]
)
class OrderSystemGroupedListView(ListAPIView):
    serializer_class = OrderSystemGroupedSerializer
    
    def get_queryset(self):
        oc_number = self.kwargs['oc_number']
        queryset = OrderSystem.objects.filter(oc_number=oc_number)

        # Verifica se a ordem de compra existe
        if not queryset.exists():
            return queryset.none()  # Retorna uma queryset vazia
        
        # Dados agrupados
        first = queryset.first()
        data = {
            'oc_number': first.oc_number,
            'store': first.store.code,
            'store_name': first.store.name,
            'supplier': first.supplier.code,
            'supplier_name': first.supplier.name,
            'total_amount': first.total_amount,
            'date': first.date,
            'expected_date': first.expected_date,
            'items': OrderSystemItemSerializer(queryset, many=True).data
        }
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'detail': 'OC não encontrada.'}, status=404)
        
        return Response(queryset)

@extend_schema(
    responses=OrderDetailStockSerializer,
    summary="Lista as informações iniciais para fazer uma ordem de compra",
    description="Retorna um JSON com todas as informações iniciais para fazer a análise e a ordem de compra.",
    tags=["orders"],
    parameters=[
        OpenApiParameter(
            name='store',
            type=int,
            location=OpenApiParameter.QUERY,
            description="Código da loja",
            required=True
        ),
        OpenApiParameter(
            name='supplier',
            type=str,
            location=OpenApiParameter.QUERY,
            description="Código do fornecedor",
            required=True
        ),
        OpenApiParameter(
            name='section',
            type=str,
            location=OpenApiParameter.QUERY,
            description="Código da section",
            required=True
        ),
        OpenApiParameter(
            name='start_date_prediction',
            type=str,
            location=OpenApiParameter.QUERY,
            description="Data inicial da previsão de vendas (YYYY-MM-DD)",
            required=True
        ),
        OpenApiParameter(
            name='end_date_prediction',
            type=str,
            location=OpenApiParameter.QUERY,
            description="Data Final da previsão de vendas (YYYY-MM-DD)",
            required=True
        )                
    ]
)
class OrderDetailStockListAPIView(ListAPIView):
    serializer_class = OrderDetailStockSerializer

    def get_queryset(self):
        store_code = self.request.query_params.get('store')
        supplier = self.request.query_params.get('supplier')
        section_id = self.request.query_params.get('section')
        subsection_id = self.request.query_params.get('subsection')
        start_date_prediction = self.request.query_params.get('start_date_prediction')
        end_date_prediction = self.request.query_params.get('end_date_prediction')

        # Verifica se todos os parâmetros foram passados
        if not all([store_code, supplier, section_id]):
            raise ValidationError({'error': 'Parâmetros store, supplier e section são obrigatórios'})

        try:
            # Busca a loja com o código fornecido
            store = Store.objects.get(code=store_code)
        except Store.DoesNotExist:
            raise ValidationError({'error': f'Loja com código {store_code} não encontrada'})

        try:
            # Busca a seção pelo ID fornecido
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            raise ValidationError({'error': f'Seção com ID {section_id} não encontrada'})

        # Filtra os itens com base no fornecedor e no nome da seção
        if subsection_id:
            subsection = Subsection.objects.get(id=subsection_id)
            items = Item.objects.filter(supplier=supplier, section=section.name, subsection=subsection.name, is_disabled_purchase=False, is_disabled=False).order_by('name')
        else:
            items = Item.objects.filter(supplier=supplier, section=section.name, is_disabled_purchase=False, is_disabled=False).order_by('name')

        # Para cada item, buscamos os dados de ItemControlStock e retornamos como um queryset
        item_info = []

        for item in items:
            # Obtém os dados do ItemControlStock para o item e a loja
            item_control = ItemControlStock.objects.filter(item=item, store=store).first()
            prediction_total = sales_forecast(item.code, store.code, start_date_prediction, end_date_prediction)

            item_info.append({
                'item_code': item.code,
                'item_name': item.name,
                'pack_size': item.pack_size,
                'cost_price': item.cost_price,
                'purchase_price': item.purchase_price,
                'stock_available': item_control.stock_available if item_control else 0,
                'date_last_purchase': item_control.date_last_purchase if item_control else None,
                'quantity_last_purchase': item_control.quantity_last_purchase if item_control else 0,
                'sale_prediction': prediction_total,
                'quantity_suggested': 0,
                'current_stock_days': 0,
                'days_stock': item_control.days_stock if item_control else 0,
            })

        # Retorna os dados coletados
        print(f"[OrderDetailStockListAPIView] Itens retornados: {len(item_info)}")
        return item_info

class OrderListCreateAPIView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user, date=date.today())

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        order = serializer.instance 
        
        OrderLog.objects.create(
            order=order,
            action='created',
            user=self.request.user,
            notes='Ordem de compra criada.'
        )

        # Notificar todos os compradores
        compradores = User.objects.annotate(
            group_name_lower=Lower('groups__name')
        ).filter(group_name_lower='analista')
        for user in compradores:
            print(f'Comprador: {user.get_full_name()}')
            Notification.objects.create(
                user=user,
                title="Nova Ordem de Compra",
                message=f"Ordem de Compra #{order.id} criada por {request.user.get_full_name()}",
                type="info",
                link=f"/ordens-compra/{order.id}/"
            )     
           
        return Response({
            'order_id': order.id,
            'status_id': order.status.id,
            'status_name': order.status.status
        }, status=status.HTTP_201_CREATED, headers=headers)

class OrderRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [ GlobalDefaultPermission,  ]
    permission_classes = [IsAuthenticated, GlobalDefaultPermission, CustomOrderPermission, ]
    lookup_field = 'pk'

@extend_schema(
    summary="Listar ordens de compra com filtros",
    description="Filtra ordens por supplier, section, buyer e status (todos opcionais).",
    parameters=[
        OpenApiParameter(name='supplier', description='ID do fornecedor', required=False, type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='section', description='ID da seção', required=False, type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='buyer', description='ID do comprador', required=False, type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='status', description='ID do status', required=False, type=int, location=OpenApiParameter.QUERY),
    ],
    tags=["orders"]
)

class OrderPendingListView(ListAPIView):
    serializer_class = OrderPendingSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        supplier_id = self.request.query_params.get('supplier')
        section_id = self.request.query_params.get('section')
        buyer_id = self.request.query_params.get('buyer')
        status_id = self.request.query_params.get('status')
        pending_only = self.request.query_params.get('pending_only')

        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        if buyer_id:
            queryset = queryset.filter(buyer_id=buyer_id)
               
        if pending_only == 'true':
            queryset = queryset.filter(status_id__in=[1, 2])

        return queryset

class OrderBulkUpdateStatusView(UpdateAPIView):
    serializer_class = OrderBulkUpdateStatusSerializer
    permission_classes = [IsAuthenticated, CustomOrderPermission, ]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        orders = Order.objects.filter(id__in=ids).select_related('status')
        updated_ids = []
        user = request.user

        for order in orders:
            current_status = order.status
            next_status = OrderStatus.objects.filter(
                is_active=True,
                id__gt=current_status.id  # ou outro critério
            ).order_by('id').first()

            if next_status:
                order.status = next_status
                order.save(update_fields=['status'])
                updated_ids.append(order.id)
                
            # Log da mudança
            OrderLog.objects.create(
                order=order,
                action='status_changed',
                user=user,
                previous_status=current_status,
                new_status=next_status,
                notes='Status alterado via bulk update'
            )                

        return Response(
            {
                'message': f'{len(updated_ids)} orders atualizadas para o próximo status.',
                'updated_order_ids': updated_ids
            },
            status=status.HTTP_200_OK
        )

class OrderExportExcelView(GenericAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        order = self.get_object()

        wb = Workbook()
        ws = wb.active
        ws.title = 'Ordem de Compra'

        # Cabeçalhos
        headers = ['codigo', 'compra', 'bonificaciones', 'descuentos']
        ws.append(headers)

        # Filtrando itens com compra ou bonificação > 0
        items = order.items.filter(quantity_order__gt=0) | order.items.filter(bonus__gt=0)

        for item in items:
            ws.append([
                item.item.code,
                item.quantity_order,
                item.bonus,
                float(item.discount) if item.discount else 0.0
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=compra_{order.id}.xlsx'
        wb.save(response)

        return response

class OrderLogListView(ListAPIView):
    serializer_class = OrderLogSerializer

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        return OrderLog.objects.filter(
            order__id=order_id
        ).exclude(field_changed='total_amount').order_by('-timestamp')
