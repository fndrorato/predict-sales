import os
import json
import pandas as pd
import xgboost as xgb
from datetime import datetime
from django.conf import settings
from django.db.models import Sum
from sales.models import SalesForecast


def sales_forecast(item_code, store_id, start_date, end_date):
    """
    Retorna a previsão de vendas para o item_code no período informado.
    """
    
    forecasts = SalesForecast.objects.filter(
        item_id=item_code,
        store_id=store_id,
        forecast_date__range=[start_date, end_date],
        is_active=True
    ).order_by('forecast_date')

    if not forecasts.exists():
        return 0

    aggregate = forecasts.aggregate(total=Sum('best_prediction'))
    result = aggregate.get('total') or 0
    
    print(f"[sales_forecast] {start_date} - {end_date} - {item_code} - {store_id} = {result}")
    
    return result

# def sales_prediction(item_code, start_date, end_date):
#     """
#     Returns the total predicted sales for the given item_code between start_date and end_date.
#     """
#     if item_code == "8285":
#         print(f"[sales_prediction] {start_date} - {end_date} - {item_code}")
        
#     model_path = os.path.join(settings.BASE_DIR, "modelos", f"modelo_{item_code}.json")
    
#     if not os.path.exists(model_path):
#         return 0

#     try:
#         model = xgb.XGBRegressor()
#         model.load_model(model_path)

#         future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
#         future_df = pd.DataFrame({'ds': future_dates})
#         future_df['year'] = future_df['ds'].dt.year
#         future_df['month'] = future_df['ds'].dt.month
#         future_df['week'] = future_df['ds'].dt.isocalendar().week
#         future_df['is_weekend'] = future_df['ds'].dt.weekday >= 5
#         future_df['is_week_holiday'] = 0
#         future_df['is_week_payday'] = future_df['ds'].dt.day.isin([1, 5, 10, 15, 20, 25])
#         future_df['is_holiday'] = 0

#         features = ['year', 'month', 'week', 'is_holiday', 'is_weekend', 'is_week_holiday', 'is_week_payday']
#         future_X = future_df[features]

#         # Fazer previsão
#         preds = model.predict(future_X)        
#         # preds = model.predict(future_df[features])
#         return round(preds.sum(), 0)
    
#     except Exception as e:
#         print(f"[predict_sales_total] Error for item {item_code}: {e}")
#         return 0

def sales_prediction_by_week(item_code, start_date, end_date):
    """
    Retorna a previsão de vendas por semana no período informado.
    """
    model_path = os.path.join(settings.BASE_DIR, "modelos", f"modelo_{item_code}.json")
    if not os.path.exists(model_path):
        return []

    try:
        model = xgb.XGBRegressor()
        model.load_model(model_path)

        future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        future_df = pd.DataFrame({'ds': future_dates})
        future_df['year'] = future_df['ds'].dt.year
        future_df['month'] = future_df['ds'].dt.month
        future_df['week'] = future_df['ds'].dt.isocalendar().week
        future_df['week_start'] = future_df['ds'] - pd.to_timedelta(future_df['ds'].dt.weekday, unit='D')
        future_df['is_weekend'] = future_df['ds'].dt.weekday >= 5
        future_df['is_week_holiday'] = 0
        future_df['is_week_payday'] = future_df['ds'].dt.day.isin([1, 5, 10, 15, 20, 25])
        future_df['is_holiday'] = 0

        features = ['year', 'month', 'week', 'is_holiday', 'is_weekend', 'is_week_holiday', 'is_week_payday']
        future_X = future_df[features]
        preds = model.predict(future_X)

        future_df['prediction'] = preds
        grouped = future_df.groupby('week_start')['prediction'].sum().reset_index()
        grouped['prediction'] = grouped['prediction'].round(2)

        return grouped.to_dict(orient='records')
    except Exception as e:
        print(f"[predict_sales_by_week] Error for item {item_code}: {e}")
        return []
