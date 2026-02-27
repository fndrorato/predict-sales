from datetime import datetime
from rest_framework import serializers
from sales.models import SalesForecast


class ItemSalesStatsSerializer(serializers.Serializer):
    item_name = serializers.CharField()
    total_last_30_days = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_last_30_days = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_daily_last_8_weeks = serializers.DecimalField(max_digits=10, decimal_places=2)
    weekly_sales_last_8_weeks = serializers.ListField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )

class ForecastItemSerializer(serializers.Serializer):
    """Serializer para um item individual de previsão"""
    
    store_id = serializers.IntegerField(min_value=1)
    codigo = serializers.IntegerField(min_value=1, source='item_id')
    data = serializers.CharField()  # Aceita string para conversão flexível
    
    # Previsões dos modelos (opcionais)
    Prophet = serializers.FloatField(required=False, allow_null=True, min_value=0)
    ARIMA = serializers.FloatField(required=False, allow_null=True, min_value=0)
    XGBoost = serializers.FloatField(required=False, allow_null=True, min_value=0)
    
    # Campo com hífen precisa ser tratado diferente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar campo Holt-Winters dinamicamente
        self.fields['Holt-Winters'] = serializers.FloatField(
            required=False, allow_null=True, min_value=0
        )
    
    # Metadados opcionais
    confidence_score = serializers.FloatField(required=False, min_value=0, max_value=100)
    rmse = serializers.FloatField(required=False, min_value=0)
    mape = serializers.FloatField(required=False, min_value=0)
    
    def validate_data(self, value):
        """Valida e converte o campo data"""
        if isinstance(value, str):
            try:
                # Tentar formato DD/MM/YYYY
                return datetime.strptime(value, '%d/%m/%Y').date()
            except ValueError:
                try:
                    # Tentar formato YYYY-MM-DD
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    raise serializers.ValidationError(
                        "Formato de data inválido. Use DD/MM/YYYY ou YYYY-MM-DD"
                    )
        return value
    
    def validate(self, attrs):
        """Validação geral do item"""
        # Verificar se pelo menos um modelo tem previsão
        model_predictions = [
            attrs.get('Prophet'),
            attrs.get('ARIMA'),
            attrs.get('Holt-Winters'),
            attrs.get('XGBoost')
        ]
        
        if not any(pred is not None and pred >= 0 for pred in model_predictions):
            raise serializers.ValidationError(
                "Pelo menos um modelo deve ter uma previsão válida"
            )
        
        return attrs

class ForecastBulkSerializer(serializers.Serializer):
    """Serializer para criação em lote"""
    
    forecasts = ForecastItemSerializer(many=True)
    model_version = serializers.CharField(required=False, max_length=20)
    
    def validate_forecasts(self, value):
        """Valida lista de previsões"""
        if not value:
            raise serializers.ValidationError("Lista de previsões não pode estar vazia")
        
        if len(value) > 10000:  # Limite de segurança
            raise serializers.ValidationError("Máximo 10.000 previsões por lote")
        
        return value

class SalesForecastSerializer(serializers.ModelSerializer):
    """Serializer para o modelo SalesForecast"""
    
    forecast_date_formatted = serializers.SerializerMethodField()
    accuracy_percentage = serializers.SerializerMethodField()
    forecast_age_days = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesForecast
        fields = [
            'id', 'store_id', 'item_id', 'forecast_date', 'forecast_date_formatted',
            'prophet_prediction', 'arima_prediction', 'holt_winters_prediction', 
            'xgboost_prediction', 'best_model', 'best_prediction', 'confidence_score',
            'model_rmse', 'model_mape', 'created_at', 'updated_at', 'model_version',
            'is_active', 'actual_sales', 'forecast_error', 'accuracy_percentage',
            'forecast_age_days'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'forecast_error']
    
    def get_forecast_date_formatted(self, obj):
        return obj.forecast_date.strftime('%d/%m/%Y')
    
    def get_accuracy_percentage(self, obj):
        return obj.accuracy_percentage
    
    def get_forecast_age_days(self, obj):
        return obj.forecast_age_days
