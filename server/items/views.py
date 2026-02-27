import base64
import json
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers, status as http_status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.cache import cache
from django.db.models import Prefetch, Q
from urllib.parse import urlencode
from items.models import Item, ItemControlStock, Section
from items.serializers import (
    ItemSerializer, 
    ItemControlStockSerializer,
    SectionSerializer,
    ItemViewSerializer,
    ItemControlStockErrorSerializer,
)
from items.pagination import SingleItemCursorPagination


class ItemListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    pagination_class = SingleItemCursorPagination

    def generate_cursor(self, code):
        # Gera um cursor codificado em base64 com base no código do item
        position = {
            'reverse': False,
            'offset': 0,
            'position': [code]
        }
        return base64.b64encode(json.dumps(position).encode()).decode()

    def get_queryset(self):
        # Base queryset com prefetch_related
        queryset = Item.objects.prefetch_related(
            Prefetch('itemcontrolstock_set', queryset=ItemControlStock.objects.all())
        ).order_by('code')

        # Filtra pelo código se o parâmetro `code` for fornecido
        code = self.request.query_params.get('code')
        if code:
            queryset = queryset.filter(code=code)

        return queryset

    def get_first_last_items(self, request):
        first_item = Item.objects.order_by('code').first()
        last_item = Item.objects.order_by('-code').first()

        base_url = request.build_absolute_uri(request.path)

        def build_cursor_url(item):
            if not item:
                return None
            cursor = self.generate_cursor(item.code)
            return f"{base_url}?cursor={cursor}"

        return {
            'first': build_cursor_url(first_item),
            'last': build_cursor_url(last_item)
        }

    def list(self, request, *args, **kwargs):
        # Se tiver parâmetro `code`, converte para cursor
        code = request.query_params.get('code')
        if code and 'cursor' not in request.query_params:
            cursor = self.generate_cursor(code)
            request.GET._mutable = True
            request.GET['cursor'] = cursor
            request.GET._mutable = False

        # Checa cache
        cache_key = f"items_cursor_{request.query_params.get('cursor', 'first')}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Gera resultado normal + navegação
        try:
            response = super().list(request, *args, **kwargs)
        except KeyError as e:
            # Trata o erro de prefetching
            print(f"Erro no prefetching: {e}")
            return Response(
                {"detail": "Erro ao processar os dados relacionados."},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        first_last_links = self.get_first_last_items(request)
        response.data.update(first_last_links)

        # Cache de 60 segundos
        cache.set(cache_key, response.data, timeout=60)
        return response


class ItemControlStockUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        item_code = kwargs.get('code')
        store_data = request.data

        # Procurando o item pelo código
        try:
            item = Item.objects.get(code=item_code)
        except Item.DoesNotExist:
            return Response({"error": "Item with the given code not found."}, status=http_status.HTTP_404_NOT_FOUND)
        
        # Procurando os registros do ItemControlStock para o item fornecido
        item_control_stocks = ItemControlStock.objects.filter(item=item)

        if not item_control_stocks.exists():
            return Response({"error": "ItemControlStock not found for the given item."}, status=http_status.HTTP_404_NOT_FOUND)

        updated_items = []
        for data in store_data:
            store_id = data.get('store')
            days_stock = data.get('days_stock')
            stock_min = data.get('stock_min')
            
            # Procurando o ItemControlStock correspondente à loja
            item_control_stock = item_control_stocks.filter(store_id=store_id).first()
            
            if item_control_stock:
                item_control_stock.days_stock = days_stock
                item_control_stock.stock_min = stock_min
                item_control_stock.save()
                updated_items.append(ItemControlStockSerializer(item_control_stock).data)
            else:
                return Response({"error": f"Store {store_id} not found for the given item."}, status=http_status.HTTP_404_NOT_FOUND)
        
        return Response(updated_items, status=http_status.HTTP_200_OK)


class SectionListView(ListAPIView):
    queryset = Section.objects.all().order_by('name')
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    summary="Buscar item(s)",
    description="Busca um item pelo código exato ou vários pelo nome (contendo a palavra).",
    parameters=[
        OpenApiParameter(name='code', description='Código exato do item', required=False, type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='query', description='Busca por nome (ex: NISSIN)', required=False, type=str, location=OpenApiParameter.QUERY),
    ],
    tags=['items'],
    responses=ItemViewSerializer(many=True)
)
class ItemDetailListView(ListAPIView):
    serializer_class = ItemViewSerializer

    def get_queryset(self):
        code = self.request.query_params.get('code')
        query = self.request.query_params.get('query')

        if code:
            return Item.objects.filter(code=code)

        if query:
            return Item.objects.filter(name__icontains=query, is_disabled=False)

        raise ValidationError({'error': 'Informe ao menos um parâmetro: "code" ou "query".'})

class ItemControlStockErrorListView(ListAPIView):
    serializer_class = ItemControlStockErrorSerializer

    def get_queryset(self):
        return ItemControlStock.objects.filter(
            stock_available__lt=0,
            item__is_disabled=False,
            item__is_disabled_purchase=False
        ).filter(
            ~Q(item__section__in=['INSUMO', 'ADMINISTRATIVO'])
        )
