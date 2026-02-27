from django.urls import path
from sales.views import (
    ItemSalesStatsView,
    WeeklySalesPredictionAPIView,
    AccuracyReportAPIView,
    ForecastBulkCreateAPIView,
    ForecastByStoreAPIView,
    ForecastByItemAPIView,
    ForecastByStoreItemAPIView,
    SalesForecastViewSet,
    UpdateActualSalesAPIView,
    quick_forecast_create
)


urlpatterns = [
    path('sales/reports/item-prediction', WeeklySalesPredictionAPIView.as_view(), name='item-sales-weekly-prediction'),
    path('sales/item-stats/', ItemSalesStatsView.as_view(), name='item-sales-stats'),
    
    # Endpoints especiais
    path('forecasts/bulk-create/', ForecastBulkCreateAPIView.as_view(), name='forecast-bulk-create'),
    path('forecasts/quick-create/', quick_forecast_create, name='forecast-quick-create'),

    
    # Listar e criar previsões
    path('forecasts/', SalesForecastViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='forecast-list'),
    
    # Detalhe, atualização e remoção de previsão específica
    path('forecasts/<int:pk>/', SalesForecastViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='forecast-detail'),
    
    # === ENDPOINTS DE ESTATÍSTICAS E RELATÓRIOS ===
    
    # Estatísticas gerais
    path('forecasts/stats/', SalesForecastViewSet.as_view({
        'get': 'stats'
    }), name='forecast-stats'),
    
    # Resumo por loja
    path('forecasts/summary/', SalesForecastViewSet.as_view({
        'get': 'summary'
    }), name='forecast-summary'),
    
    # Limpeza de previsões antigas
    path('forecasts/cleanup/', SalesForecastViewSet.as_view({
        'post': 'cleanup'
    }), name='forecast-cleanup'),
    
    # === ENDPOINTS ESPECÍFICOS POR LOJA/ITEM ===
    
    # Previsões de uma loja específica
    path('forecasts/store/<int:store_id>/', ForecastByStoreAPIView.as_view(), name='forecast-by-store'),
    
    # Previsões de um item específico
    path('forecasts/item/<int:item_id>/', ForecastByItemAPIView.as_view(), name='forecast-by-item'),
    
    # Previsões de um item em uma loja específica
    path('forecasts/store/<int:store_id>/item/<int:item_id>/', ForecastByStoreItemAPIView.as_view(), name='forecast-by-store-item'),
    
    # === ENDPOINTS DE VALIDAÇÃO E COMPARAÇÃO ===
    
    # Atualizar vendas reais para comparação
    path('forecasts/update-actual-sales/', UpdateActualSalesAPIView.as_view(), name='forecast-update-actual-sales'),
    
    # Relatório de acurácia
    path('forecasts/accuracy-report/', AccuracyReportAPIView.as_view(), name='forecast-accuracy-report'),
]
