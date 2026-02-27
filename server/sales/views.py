import logging
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Count, Avg, Sum, Min, Max, Q
from django.db.models.functions import TruncWeek
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from items.models import Item
from sales.models import Sale, SalesForecast
from sales.serializers import (
    ItemSalesStatsSerializer,
    SalesForecastSerializer,
    ForecastBulkSerializer,
)
from stores.models import Store
from utils.predictions import sales_prediction_by_week
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


logger = logging.getLogger(__name__)

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='item',
            type=OpenApiTypes.INT,
            required=True,
            location=OpenApiParameter.QUERY,
            description='ID do item a ser consultado'
        ),
        OpenApiParameter(
            name='store',
            type=OpenApiTypes.INT,
            required=True,
            location=OpenApiParameter.QUERY,
            description='ID da loja para filtro de vendas'
        ),
    ],
    description="Retorna estatísticas de venda de um item em uma loja específica nos últimos 30 dias e 8 semanas.",
    responses={200: ItemSalesStatsSerializer}
)
class ItemSalesStatsView(ListAPIView):
    serializer_class = ItemSalesStatsSerializer

    def list(self, request, *args, **kwargs):
        item_id = request.query_params.get('item')
        store_id = request.query_params.get('store')

        if not item_id or not store_id:
            return Response({'error': 'Item ID and Store ID are required.'}, status=400)

        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        eight_weeks_ago = today - timedelta(weeks=8)

        sales_qs = Sale.objects.filter(
            item_id=item_id,
            store_id=store_id,
            date__gte=eight_weeks_ago,
        )

        # Nome do item
        item_name = sales_qs.first().item.name if sales_qs.exists() else ""

        # Total últimos 30 dias
        last_30_days_sales = sales_qs.filter(date__gte=thirty_days_ago)
        total_last_30_days = last_30_days_sales.aggregate(total=Sum('quantity'))['total'] or 0

        # Média diária últimos 30 dias
        average_last_30_days = total_last_30_days / 30

        # Venda por semana (últimas 8 semanas)
        weekly_sales = []
        total_8_weeks = 0
        for i in range(8):
            start_date = today - timedelta(weeks=(i + 1))
            end_date = today - timedelta(weeks=i)
            week_total = sales_qs.filter(date__gte=start_date, date__lt=end_date).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            total_8_weeks += week_total

            label = f"{start_date.strftime('%d/%m')}-{end_date.strftime('%d/%m')}"
            weekly_sales.insert(0, {'week': label, 'total': str(round(week_total, 2))})

        average_daily_last_8_weeks = total_8_weeks / 56  # 8 semanas * 7 dias
        
        data = {
            'item_name': item_name,
            'total_last_30_days': round(total_last_30_days, 2),
            'average_last_30_days': round(average_last_30_days, 2),
            'average_daily_last_8_weeks': round(average_daily_last_8_weeks, 2),
            'weekly_sales_last_8_weeks': weekly_sales,
        }

        return Response(data)

class WeeklySalesPredictionAPIView(APIView):

    @extend_schema(
        summary="Vendas reais e previsão de vendas por semana",
        description="Retorna um JSON com as vendas reais e previstas por semana, para um item em uma loja específica.",
        tags=["sales"],
        parameters=[
            OpenApiParameter(name='store', type=int, required=True),
            OpenApiParameter(name='item', type=str, required=True),
            OpenApiParameter(name='start_date', type=str, required=True),
            OpenApiParameter(name='end_date', type=str, required=True),
        ]
    )
    def get(self, request):
        store_code = request.query_params.get('store')
        item_code = request.query_params.get('item')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not all([store_code, item_code, start_date, end_date]):
            raise ValidationError("Parâmetros 'store', 'item', 'start_date' e 'end_date' são obrigatórios.")

        try:
            store = Store.objects.get(code=store_code)
            item = Item.objects.get(code=item_code)
        except (Store.DoesNotExist, Item.DoesNotExist):
            raise ValidationError("Loja ou Item não encontrado.")

        # VENDAS REAIS
        sales_qs = Sale.objects.filter(
            store=store,
            item=item,
            date__range=[start_date, end_date]
        ).annotate(
            week=TruncWeek('date')
        ).values('week').annotate(
            total=Sum('quantity')
        ).order_by('week')

        sales_by_week = {s['week']: float(s['total']) for s in sales_qs}

        # PREVISÃO DE VENDAS
        predictions = sales_prediction_by_week(item_code, start_date, end_date)
        result = []

        for entry in predictions:
            week_start = entry['week_start']
            result.append({
                'week': week_start.strftime('%Y-%m-%d'),
                'sales': round(sales_by_week.get(week_start.date(), 0), 2),
                'prediction': entry['prediction']
            })

        return Response(result)

class ForecastBulkCreateAPIView(APIView):
    """
    API otimizada para criação em lote usando DRF
    POST /api/v1/forecasts/bulk-create/
    """
    
    permission_classes = [IsAuthenticated]  # Adicione autenticação se necessário
    
    def post(self, request):
        """Criar previsões em lote"""
        
        # Validar dados de entrada
        serializer = ForecastBulkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Dados inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        forecasts_data = validated_data['forecasts']
        model_version = validated_data.get('model_version', datetime.now().strftime('%Y%m%d_%H%M'))
        
        # Processar em lote
        try:
            result = self._process_bulk_forecasts(forecasts_data, model_version)
            
            # Log de sucesso
            logger.info(
                f"Bulk forecast create by user {request.user.id if request.user.is_authenticated else 'anonymous'}: "
                f"{result['created']} created, {result['updated']} updated, {result['errors']} errors"
            )
            
            response_status = status.HTTP_201_CREATED if result['errors'] == 0 else status.HTTP_207_MULTI_STATUS
            
            return Response({
                'status': 'success',
                'message': 'Previsões processadas com sucesso',
                'summary': result
            }, status=response_status)
            
        except Exception as e:
            logger.error(f"Erro no bulk create: {e}")
            return Response({
                'status': 'error',
                'message': f'Erro interno do servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_bulk_forecasts(self, forecasts_data, model_version):
        """Processa lista de previsões em transação"""
        
        created_count = 0
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for i, forecast_data in enumerate(forecasts_data):
                try:
                    result = self._create_or_update_forecast(forecast_data, model_version)
                    if result == 'created':
                        created_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    errors.append({
                        'index': i,
                        'store_id': forecast_data.get('store_id'),
                        'item_id': forecast_data.get('item_id'),
                        'error': str(e)
                    })
                    
                    # Falha rápida se muitos erros
                    if len(errors) > 100:
                        raise Exception(f"Muitos erros detectados ({len(errors)}). Processamento abortado.")
        
        return {
            'total_processed': len(forecasts_data),
            'created': created_count,
            'updated': updated_count,
            'errors': len(errors),
            'error_details': errors[:10] if errors else []  # Limitar detalhes
        }
    
    def _create_or_update_forecast(self, forecast_data, model_version):
        """Cria ou atualiza uma previsão individual"""
        
        # Extrair dados
        store_id = forecast_data['store_id']
        item_id = forecast_data['item_id']
        forecast_date = forecast_data['data']
        
        # Extrair previsões
        prophet_pred = forecast_data.get('Prophet')
        arima_pred = forecast_data.get('ARIMA')
        holt_winters_pred = forecast_data.get('Holt-Winters')
        xgboost_pred = forecast_data.get('XGBoost')
        
        # Determinar melhor modelo
        best_model, best_prediction = self._determine_best_model(
            prophet_pred, arima_pred, holt_winters_pred, xgboost_pred
        )
        
        # Criar ou atualizar
        forecast_obj, created = SalesForecast.objects.update_or_create(
            store_id=store_id,
            item_id=item_id,
            forecast_date=forecast_date,
            model_version=model_version,
            defaults={
                'prophet_prediction': prophet_pred,
                'arima_prediction': arima_pred,
                'holt_winters_prediction': holt_winters_pred,
                'xgboost_prediction': xgboost_pred,
                'best_model': best_model,
                'best_prediction': best_prediction,
                'confidence_score': forecast_data.get('confidence_score', 85.0),
                'model_rmse': forecast_data.get('rmse'),
                'model_mape': forecast_data.get('mape'),
                'is_active': True
            }
        )
        
        return 'created' if created else 'updated'
    
    def _determine_best_model(self, prophet, arima, holt_winters, xgboost):
        """Determina melhor modelo com lógica aprimorada"""
        
        models = [
            ('Prophet', prophet),
            ('ARIMA', arima),
            ('Holt-Winters', holt_winters),
            ('XGBoost', xgboost)
        ]
        
        # Filtrar modelos válidos
        valid_models = [(name, value) for name, value in models if value is not None and value >= 0]
        
        if not valid_models:
            raise ValueError("Nenhuma previsão válida encontrada")
        
        # Prioridade: Prophet > XGBoost > Holt-Winters > ARIMA
        priority = ['Prophet', 'XGBoost', 'Holt-Winters', 'ARIMA']
        
        for preferred_model in priority:
            for name, value in valid_models:
                if name == preferred_model:
                    return name, value
        
        # Fallback para o primeiro válido
        return valid_models[0]

# =============================================================================
# VIEWSET PARA CRUD COMPLETO
# =============================================================================

class SalesForecastViewSet(ModelViewSet):
    """
    ViewSet completo para CRUD de previsões
    GET    /api/v1/forecasts/         - Listar
    POST   /api/v1/forecasts/         - Criar individual
    GET    /api/v1/forecasts/{id}/    - Detalhe
    PUT    /api/v1/forecasts/{id}/    - Atualizar
    DELETE /api/v1/forecasts/{id}/    - Deletar
    """
    
    queryset = SalesForecast.objects.all()
    serializer_class = SalesForecastSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtros avançados
    filterset_fields = ['store_id', 'item_id', 'best_model', 'is_active']
    search_fields = ['store_id', 'item_id']
    ordering_fields = ['forecast_date', 'created_at', 'best_prediction', 'confidence_score']
    ordering = ['-forecast_date', 'store_id', 'item_id']
    
    def get_queryset(self):
        """Queryset customizado com filtros extras"""
        queryset = super().get_queryset()
        
        # Filtros por parâmetros de query
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        model_version = self.request.query_params.get('model_version')
        min_confidence = self.request.query_params.get('min_confidence')
        
        if date_from:
            queryset = queryset.filter(forecast_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(forecast_date__lte=date_to)
        if model_version:
            queryset = queryset.filter(model_version=model_version)
        if min_confidence:
            queryset = queryset.filter(confidence_score__gte=float(min_confidence))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para estatísticas
        GET /api/v1/forecasts/stats/
        """
        
        queryset = self.get_queryset().filter(is_active=True)
        
        # Estatísticas gerais
        general_stats = queryset.aggregate(
            total_forecasts=Count('id'),
            total_stores=Count('store_id', distinct=True),
            total_items=Count('item_id', distinct=True),
            avg_confidence=Avg('confidence_score'),
            total_predicted_sales=Sum('best_prediction'),
            min_date=Min('forecast_date'),
            max_date=Max('forecast_date')
        )
        
        # Distribuição por modelo
        model_distribution = list(
            queryset.values('best_model')
            .annotate(count=Count('id'), avg_confidence=Avg('confidence_score'))
            .order_by('-count')
        )
        
        # Top lojas por previsão
        top_stores = list(
            queryset.values('store_id')
            .annotate(
                total_items=Count('item_id', distinct=True),
                total_prediction=Sum('best_prediction'),
                avg_confidence=Avg('confidence_score')
            )
            .order_by('-total_prediction')[:10]
        )
        
        return Response({
            'general_stats': {
                **general_stats,
                'avg_confidence': round(general_stats['avg_confidence'] or 0, 2),
                'total_predicted_sales': round(general_stats['total_predicted_sales'] or 0, 2),
                'min_date': general_stats['min_date'].strftime('%Y-%m-%d') if general_stats['min_date'] else None,
                'max_date': general_stats['max_date'].strftime('%Y-%m-%d') if general_stats['max_date'] else None,
            },
            'model_distribution': model_distribution,
            'top_stores': top_stores
        })
    
    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """
        Endpoint para limpeza de previsões antigas
        POST /api/v1/forecasts/cleanup/
        """
        
        days_old = int(request.data.get('days_old', 30))
        cutoff_date = datetime.now().date() - timedelta(days=days_old)
        
        # Desativar previsões antigas
        updated = SalesForecast.objects.filter(
            created_at__date__lt=cutoff_date,
            is_active=True
        ).update(is_active=False)
        
        logger.info(f"Cleanup por usuário {request.user.id}: {updated} previsões desativadas")
        
        return Response({
            'message': f'{updated} previsões antigas desativadas',
            'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
            'days_old': days_old
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Endpoint para resumo por loja/período
        GET /api/v1/forecasts/summary/?store_id=1&date_from=2025-08-01
        """
        
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response({
                'error': 'store_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        summary = SalesForecast.get_forecast_summary(
            store_id=int(store_id),
            date_from=request.query_params.get('date_from'),
            date_to=request.query_params.get('date_to')
        )
        
        return Response(summary)

# =============================================================================
# FUNÇÃO VIEW SIMPLES PARA CASOS ESPECÍFICOS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_forecast_create(request):
    """
    View simplificada para criação rápida
    POST /api/v1/forecasts/quick-create/
    
    Exemplo de uso para um item individual:
    {
        "store_id": 1,
        "item_id": 123,
        "forecast_date": "2025-08-01",
        "prediction": 15.5,
        "model": "Prophet"
    }
    """
    
    try:
        data = request.data
        
        forecast_obj, created = SalesForecast.objects.update_or_create(
            store_id=data['store_id'],
            item_id=data['item_id'],
            forecast_date=data['forecast_date'],
            model_version=datetime.now().strftime('%Y%m%d'),
            defaults={
                'best_model': data.get('model', 'Prophet'),
                'best_prediction': data['prediction'],
                'confidence_score': data.get('confidence_score', 85.0),
                'is_active': True
            }
        )
        
        serializer = SalesForecastSerializer(forecast_obj)
        
        return Response({
            'status': 'created' if created else 'updated',
            'forecast': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except KeyError as e:
        return Response({
            'error': f'Campo obrigatório faltando: {e}'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForecastByStoreAPIView(ListAPIView):
    '''Listar previsões de uma loja específica'''
    
    serializer_class = SalesForecastSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        store_id = self.kwargs['store_id']
        queryset = SalesForecast.objects.filter(
            store_id=store_id, 
            is_active=True
        )
        
        # Filtros opcionais
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(forecast_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(forecast_date__lte=date_to)
        
        return queryset.order_by('-forecast_date', 'item_id')

class ForecastByItemAPIView(ListAPIView):
    '''Listar previsões de um item específico'''
    
    serializer_class = SalesForecastSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        item_id = self.kwargs['item_id']
        return SalesForecast.objects.filter(
            item_id=item_id,
            is_active=True
        ).order_by('-forecast_date', 'store_id')

class ForecastByStoreItemAPIView(ListAPIView):
    '''Listar previsões de um item em uma loja específica'''
    
    serializer_class = SalesForecastSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        store_id = self.kwargs['store_id']
        item_id = self.kwargs['item_id']
        return SalesForecast.objects.filter(
            store_id=store_id,
            item_id=item_id,
            is_active=True
        ).order_by('-forecast_date')

class UpdateActualSalesAPIView(APIView):
    '''Atualizar vendas reais para comparação com previsões'''
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        '''
        Payload esperado:
        {
            "sales_data": [
                {
                    "store_id": 1,
                    "item_id": 123,
                    "date": "2025-08-01",
                    "actual_sales": 12.5
                }
            ]
        }
        '''
        
        try:
            sales_data = request.data.get('sales_data', [])
            updated_count = 0
            not_found_count = 0
            
            with transaction.atomic():
                for sale in sales_data:
                    try:
                        forecast = SalesForecast.objects.get(
                            store_id=sale['store_id'],
                            item_id=sale['item_id'],
                            forecast_date=sale['date'],
                            is_active=True
                        )
                        forecast.actual_sales = sale['actual_sales']
                        forecast.save()  # Isso vai calcular o forecast_error automaticamente
                        updated_count += 1
                        
                    except SalesForecast.DoesNotExist:
                        not_found_count += 1
            
            return Response({
                'status': 'success',
                'updated': updated_count,
                'not_found': not_found_count,
                'message': f'{updated_count} previsões atualizadas com vendas reais'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AccuracyReportAPIView(APIView):
    '''Relatório de acurácia das previsões'''
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''Gerar relatório de acurácia'''
        
        # Filtros
        store_id = request.query_params.get('store_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Query base - apenas previsões com vendas reais
        queryset = SalesForecast.objects.filter(
            is_active=True,
            actual_sales__isnull=False
        )
        
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        if date_from:
            queryset = queryset.filter(forecast_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(forecast_date__lte=date_to)
        
        # Calcular métricas
        total_forecasts = queryset.count()
        
        if total_forecasts == 0:
            return Response({
                'message': 'Nenhuma previsão com vendas reais encontrada',
                'total_forecasts': 0
            })
        
        # Métricas gerais
        total_mae = sum(abs(f.forecast_error) for f in queryset if f.forecast_error is not None)
        avg_mae = total_mae / total_forecasts if total_forecasts > 0 else 0
        
        # Acurácia por modelo
        model_accuracy = {}
        for model in ['Prophet', 'ARIMA', 'Holt-Winters', 'XGBoost']:
            model_forecasts = queryset.filter(best_model=model)
            if model_forecasts.exists():
                model_errors = [f.forecast_error for f in model_forecasts if f.forecast_error is not None]
                model_accuracy[model] = {
                    'count': len(model_errors),
                    'avg_mae': sum(model_errors) / len(model_errors) if model_errors else 0
                }
        
        return Response({
            'period': {
                'from': date_from,
                'to': date_to
            },
            'general_metrics': {
                'total_forecasts_with_actuals': total_forecasts,
                'average_mae': round(avg_mae, 2)
            },
            'model_accuracy': model_accuracy,
            'store_id': store_id
        })


