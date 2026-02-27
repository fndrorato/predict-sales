import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date, timedelta
from django.db.models import F, Max, Count
from django.utils.timezone import now
from django.utils import timezone
from items.models import Item, ItemControlStock
from orders.models import OrderSystem, OrderSystemResult
from sales.models import Sale


class DashboardStatsView(APIView):
    """Retorna estatísticas do dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        current_month_orders = OrderSystemResult.objects.filter(
            date__year=today.year,
            date__month=today.month
        )

        total_current_month = current_month_orders.count() or 1  # evitar divisão por zero

        oc_complete = current_month_orders.filter(all_items_received=1).count()
        oc_overdue = current_month_orders.filter(received_on_time=1).count()
        oc_awaiting = OrderSystemResult.objects.filter(is_open=True).count()

        items_error_stock = ItemControlStock.objects.filter(
            stock_available__lt=0,
            item__is_disabled=False,
            item__is_disabled_purchase=False
        ).count()

        data = {
            "oc_complete": f"{(oc_complete / total_current_month * 100):.2f}".replace('.', ',') + "%",
            "oc_overdue": f"{(oc_overdue / total_current_month * 100):.2f}".replace('.', ',') + "%",
            "oc_awaiting": f"{oc_awaiting:,}".replace(",", "."),
            "items_error_stock": f"{items_error_stock:,}".replace(",", ".")
        }

        return Response(data)
        data = {
            "items_with_stock_no_sales": 430,  
            "oc_awaiting": 47,  
            "oc_incomplete": 23,  
            "oc_overdue": 9
        }
        return Response(data)

class NoSalesStatsView(APIView):
    """Retorna dados de produtos sem vendas acima da frequência média"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stocks_qs = ItemControlStock.objects.select_related('item', 'store') \
            .filter(
                sales_frequency__lt=30,
                sales_frequency__isnull=False,
                stock_available__gt=0
            ).values(
                'item__code',
                'item__name',
                'item__section',  # ou categoria se existir
                'store__code',
                'store__name',
                'stock_available',
                'sales_frequency'
            )
        
        sales_qs = Sale.objects.filter(
            item_id__in=[s['item__code'] for s in stocks_qs],
            store_id__in=[s['store__code'] for s in stocks_qs]
        ).values('item_id', 'store_id').annotate(last_sale=Max('date'))
        
        df_stocks = pd.DataFrame(stocks_qs)
        df_sales = pd.DataFrame(sales_qs) 
        
        df_stocks['item__code'] = df_stocks['item__code'].astype(str)
        df_stocks['store__code'] = df_stocks['store__code'].astype(str)

        df_sales['item_id'] = df_sales['item_id'].astype(str)
        df_sales['store_id'] = df_sales['store_id'].astype(str)
           
        
        df_merged = df_stocks.merge(
            df_sales,
            left_on=['item__code', 'store__code'],
            right_on=['item_id', 'store_id'],
            how='left'
        )

        # Remover os que nunca venderam (sem last_sale)
        df_merged = df_merged[df_merged['last_sale'].notnull()]

        # Calcular dias sem venda
        df_merged['dias_sem_venda'] = (pd.to_datetime(date.today()) - pd.to_datetime(df_merged['last_sale'])).dt.days

        # Aplicar o filtro
        df_final = df_merged[df_merged['dias_sem_venda'] > df_merged['sales_frequency']]  
                       
        df_final = df_final.rename(columns={
            'item__code': 'product_code',
            'item__name': 'product_name',
            'item__section': 'category',
            'store__name': 'store',
            'stock_available': 'stock',
            'sales_frequency': 'sales_frequency',
            'last_sale': 'no_sales_since'
        })

        df_final['no_sales_since'] = pd.to_datetime(df_final['no_sales_since']).dt.strftime("%Y-%m-%d")

        return Response(df_final[[
            'product_code', 'product_name', 'category', 'store',
            'stock', 'sales_frequency', 'no_sales_since'
        ]].to_dict(orient="records"))

class OCAwaitingStatsView(APIView):
    """Retorna dados de ordens de compra aguardando"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filtra apenas ordens em aberto
        orders = OrderSystem.objects.filter(is_open=True).select_related('store', 'supplier', 'item')

        # Agrupamento por oc_number
        grouped = {}
        for order in orders:
            oc_number = order.oc_number
            if oc_number not in grouped:
                grouped[oc_number] = {
                    "order_number": f"{str(oc_number)}",
                    "store": order.store.name,
                    "supplier": order.supplier.name,
                    "date_created": order.date.strftime("%Y-%m-%d"),
                    "date_expected": order.expected_date.strftime("%Y-%m-%d"),
                    "details": [],
                    "complete_delivery": True,
                }
            grouped[oc_number]["details"].append({
                "product_code": order.item.code,
                "product_name": order.item.name,
                "quantity": float(order.quantity_order),
                "received": float(order.quantity_received),
            })
            if order.quantity_received < order.quantity_order:
                grouped[oc_number]["complete_delivery"] = False

        # Filtra apenas ordens com entrega incompleta
        incomplete_orders = [oc for oc in grouped.values() if not oc["complete_delivery"]]

        return Response(incomplete_orders)
