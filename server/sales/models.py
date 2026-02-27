from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from items.models import Item
from stores.models import Store


class Sale(models.Model):
    ticket_number = models.CharField(max_length=30)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.IntegerField()    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Calendar(models.Model):
    date = models.DateField(primary_key=True)
    is_holiday = models.BooleanField(default=False)
    holiday_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Dia do calendário"
        verbose_name_plural = "Calendário"

    def __str__(self):
        return self.date.strftime("%d/%m/%Y")

class SalesGroupView(models.Model):
    id = models.IntegerField(primary_key=True)
    store = models.ForeignKey('stores.Store', on_delete=models.DO_NOTHING)
    date = models.DateField()
    item_group = models.ForeignKey('items.ItemGroupView', on_delete=models.DO_NOTHING)
    total_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'sales_group_view'
        verbose_name = 'Sales Group View'
        verbose_name_plural = 'Sales Group Views'

class SalesForecast(models.Model):
    """
    Modelo para armazenar previsões de vendas geradas pelo sistema de ML
    Inclui previsões de TODOS os modelos + melhor modelo selecionado
    """
    
    # === IDENTIFICAÇÃO ===
    item_id = models.PositiveIntegerField(
        verbose_name="ID do Produto", 
        help_text="Identificador do produto/item"
    )
    
    store_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID da Loja",
        help_text="Identificador da loja (null = agregado todas as lojas)"
    )
    
    forecast_date = models.DateField(
        verbose_name="Data da Previsão",
        help_text="Data para qual a previsão é válida"
    )
    
    # === INFORMAÇÕES DO PRODUTO ===
    category = models.CharField(
        max_length=100,
        verbose_name="Categoria",
        help_text="Categoria do produto"
    )
    
    brand = models.CharField(
        max_length=100,
        verbose_name="Marca",
        help_text="Marca do produto"
    )
    
    # === PREVISÕES DE TODOS OS MODELOS ===
    arima_prediction = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Previsão ARIMA",
        help_text="Previsão gerada pelo modelo ARIMA"
    )
    
    holt_winters_prediction = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Previsão Holt-Winters",
        help_text="Previsão gerada pelo modelo Holt-Winters"
    )
    
    linear_regression_prediction = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Previsão Linear Regression",
        help_text="Previsão gerada pelo modelo Linear Regression"
    )
    
    prophet_prediction = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Previsão Prophet",
        help_text="Previsão gerada pelo modelo Prophet"
    )
    
    random_forest_prediction = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Previsão Random Forest",
        help_text="Previsão gerada pelo modelo Random Forest"
    )
    
    xgboost_prediction = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Previsão XGBoost",
        help_text="Previsão gerada pelo modelo XGBoost"
    )
    
    # === MELHOR MODELO E PREVISÃO FINAL ===
    best_model = models.CharField(
        max_length=50,
        choices=[
            ('arima', 'ARIMA'),
            ('holt_winters', 'Holt-Winters'),
            ('linear_regression', 'Linear Regression'),
            ('prophet', 'Prophet'),
            ('random_forest', 'Random Forest'),
            ('xgboost', 'XGBoost'),
        ],
        verbose_name="Melhor Modelo",
        help_text="Modelo que apresentou melhor performance (menor MAE)"
    )
    
    best_prediction = models.FloatField(
        validators=[MinValueValidator(0.0)],
        verbose_name="Previsão Final",
        help_text="Previsão do melhor modelo (valor a ser usado)"
    )
    
    model_mae = models.FloatField(
        validators=[MinValueValidator(0.0)],
        verbose_name="MAE do Melhor Modelo",
        help_text="Mean Absolute Error do melhor modelo"
    )
    
    # === MÉTRICAS DE QUALIDADE (CAMPOS ADICIONAIS) ===
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Score de Confiança",
        help_text="Score de confiança da previsão (0-100%)"
    )
    
    model_rmse = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="RMSE do Modelo",
        help_text="Root Mean Square Error do melhor modelo"
    )
    
    model_mape = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="MAPE do Modelo", 
        help_text="Mean Absolute Percentage Error do melhor modelo"
    )
    
    # === METADADOS ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    model_version = models.CharField(
        max_length=20,
        default="1.0",
        verbose_name="Versão do Modelo",
        help_text="Versão/timestamp do modelo que gerou a previsão"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Indica se esta previsão está ativa"
    )
    
    # === CAMPOS PARA AVALIAÇÃO POSTERIOR ===
    actual_sales = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Vendas Reais",
        help_text="Vendas reais (para comparação posterior)"
    )
    
    forecast_error = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Erro da Previsão",
        help_text="Diferença entre previsão e venda real (calculado automaticamente)"
    )
    
    class Meta:
        verbose_name = "Previsão de Vendas"
        verbose_name_plural = "Previsões de Vendas"
        
        # Constraint: Uma previsão única por item/loja/data/versão
        unique_together = [
            ['item_id', 'store_id', 'forecast_date'] 
        ]
        
        # Indexes para performance
        indexes = [
            models.Index(fields=['item_id', 'store_id', 'forecast_date']),
            models.Index(fields=['forecast_date']),
            models.Index(fields=['created_at']),
            models.Index(fields=['model_version']),
            models.Index(fields=['best_model']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
        ]
        
        # Ordenação padrão
        ordering = ['-forecast_date', 'item_id', 'store_id']
    
    def __str__(self):
        store_info = f"Loja {self.store_id}" if self.store_id else "Todas as lojas"
        return f"{store_info} - Item {self.item_id} - {self.forecast_date} ({self.best_model})"
    
    def save(self, *args, **kwargs):
        """Override save para lógica adicional"""
        # Calcular erro se temos vendas reais
        if self.actual_sales is not None and self.best_prediction is not None:
            self.forecast_error = abs(self.best_prediction - self.actual_sales)
        
        super().save(*args, **kwargs)
    
    # === PROPRIEDADES CALCULADAS ===
    @property
    def accuracy_percentage(self):
        """Calcula percentual de acurácia se há vendas reais"""
        if self.actual_sales and self.best_prediction:
            if self.actual_sales == 0:
                return 100 if self.best_prediction == 0 else 0
            error_rate = abs(self.forecast_error) / self.actual_sales
            return max(0, (1 - error_rate) * 100)
        return None
    
    @property
    def forecast_age_days(self):
        """Quantos dias desde que a previsão foi criada"""
        return (timezone.now().date() - self.created_at.date()).days
    
    @property
    def is_future_forecast(self):
        """Verifica se é uma previsão para o futuro"""
        return self.forecast_date > timezone.now().date()
    
    @property
    def days_until_forecast(self):
        """Quantos dias até a data da previsão"""
        if self.is_future_forecast:
            return (self.forecast_date - timezone.now().date()).days
        return 0
    
    @property
    def model_predictions_dict(self):
        """Retorna dicionário com todas as previsões dos modelos"""
        return {
            'arima': self.arima_prediction,
            'holt_winters': self.holt_winters_prediction,
            'linear_regression': self.linear_regression_prediction,
            'prophet': self.prophet_prediction,
            'random_forest': self.random_forest_prediction,
            'xgboost': self.xgboost_prediction,
        }
    
    @property
    def available_models_count(self):
        """Quantos modelos geraram previsões válidas"""
        predictions = self.model_predictions_dict
        return sum(1 for pred in predictions.values() if pred is not None)
    
    # === MÉTODOS DE CLASSE ===
    @classmethod
    def get_active_forecasts(cls, store_id=None, item_id=None, date_from=None, date_to=None):
        """Método helper para buscar previsões ativas"""
        queryset = cls.objects.filter(is_active=True)
        
        if store_id is not None:
            queryset = queryset.filter(store_id=store_id)
        
        if item_id:
            queryset = queryset.filter(item_id=item_id)
            
        if date_from:
            queryset = queryset.filter(forecast_date__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(forecast_date__lte=date_to)
        
        return queryset
    
    @classmethod
    def get_forecast_summary(cls, store_id=None, date_from=None, date_to=None):
        """Retorna resumo de previsões"""
        queryset = cls.objects.filter(is_active=True)
        
        if store_id is not None:
            queryset = queryset.filter(store_id=store_id)
        if date_from:
            queryset = queryset.filter(forecast_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(forecast_date__lte=date_to)
        
        return queryset.aggregate(
            total_items=Count('item_id', distinct=True),
            total_forecast=Sum('best_prediction'),
            avg_mae=Avg('model_mae'),
            avg_confidence=Avg('confidence_score'),
            
            # Contagem por modelo
            arima_count=Count('id', filter=Q(best_model='arima')),
            holt_winters_count=Count('id', filter=Q(best_model='holt_winters')),
            linear_regression_count=Count('id', filter=Q(best_model='linear_regression')),
            prophet_count=Count('id', filter=Q(best_model='prophet')),
            random_forest_count=Count('id', filter=Q(best_model='random_forest')),
            xgboost_count=Count('id', filter=Q(best_model='xgboost')),
        )
    
    @classmethod
    def get_model_performance_comparison(cls):
        """Compara performance de todos os modelos"""
        from django.db.models import Avg
        
        models_performance = {}
        model_choices = ['arima', 'holt_winters', 'linear_regression', 'prophet', 'random_forest', 'xgboost']
        
        for model in model_choices:
            queryset = cls.objects.filter(best_model=model, is_active=True)
            if queryset.exists():
                models_performance[model] = {
                    'count': queryset.count(),
                    'avg_mae': queryset.aggregate(avg_mae=Avg('model_mae'))['avg_mae'],
                    'total_prediction': queryset.aggregate(total=Sum('best_prediction'))['total'],
                }
        
        return models_performance
    
    @classmethod
    def bulk_create_from_csv(cls, csv_file_path, model_version="1.0"):
        """
        Método para importar previsões em massa do CSV gerado pelo sistema
        """
        import pandas as pd
        
        try:
            df = pd.read_csv(csv_file_path)
            forecasts_to_create = []
            
            for _, row in df.iterrows():
                forecast = cls(
                    item_id=row['item_id'],
                    store_id=row['store_id'] if pd.notna(row['store_id']) else None,
                    forecast_date=pd.to_datetime(row['forecast_date']).date(),
                    category=row['category'],
                    brand=row['brand'],
                    best_model=row['best_model'],
                    best_prediction=row['best_prediction'],
                    model_mae=row['model_mae'],
                    
                    # Previsões dos modelos individuais
                    arima_prediction=row['arima_prediction'] if pd.notna(row['arima_prediction']) else None,
                    holt_winters_prediction=row['holt_winters_prediction'] if pd.notna(row['holt_winters_prediction']) else None,
                    linear_regression_prediction=row['linear_regression_prediction'] if pd.notna(row['linear_regression_prediction']) else None,
                    prophet_prediction=row['prophet_prediction'] if pd.notna(row['prophet_prediction']) else None,
                    random_forest_prediction=row['random_forest_prediction'] if pd.notna(row['random_forest_prediction']) else None,
                    xgboost_prediction=row['xgboost_prediction'] if pd.notna(row['xgboost_prediction']) else None,
                    
                    model_version=model_version
                )
                forecasts_to_create.append(forecast)
            
            # Bulk create para performance
            cls.objects.bulk_create(forecasts_to_create, ignore_conflicts=True)
            return len(forecasts_to_create)
            
        except Exception as e:
            print(f"Erro ao importar CSV: {e}")
            return 0
