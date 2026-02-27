import logging
import multiprocessing
import mlflow
import numpy as np
import os 
import pandas as pd
import psycopg2
import psycopg2.extras
import sys
import warnings
import time
import socket
from app.utils.mlflow_wrapper import mlflow_tracker
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta
from itertools import islice
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import psycopg2.extras
from functools import partial


# Configuração de logging
try:
    from app.utils.mlflow_wrapper import mlflow_tracker
    import mlflow
    MLFLOW_AVAILABLE = True
    logging.info("✅ MLflow disponível")
except ImportError as e:
    MLFLOW_AVAILABLE = False
    logging.warning(f"⚠️  MLflow não disponível: {e}")

warnings.filterwarnings('ignore')

# Variáveis Globais de Status (ATUALIZADAS DURANTE O PROCESSAMENTO)
# O progresso total é distribuído assim: 5% (load), 85% (loop), 10% (save)
FORECAST_STATUS = {'progress': 0, 'total': 0, 'completed': 0, 'error': None, 'data': None}
FORECAST_TASK_RUNNING = False

# Variável de versão para rastrear qual script criou o forecast
MODEL_VERSION = "20251009_V1"

# Tentar importar Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# Tentar importar XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


# =============================================================================
# 1. FUNÇÕES DE ACESSO AO BANCO DE DADOS (Inalteradas)
# ...
# =============================================================================

# SUBSTITUIR A FUNÇÃO load_data COMPLETA

def load_data(pg_conn_str, store_ids=None):
    """
    Carrega os dados de vendas e calendário do PostgreSQL.
    
    Args:
        pg_conn_str: String de conexão PostgreSQL
        store_ids: Lista de store_ids para filtrar (ex: [1, 2, 3])
                   Se None, carrega todas as lojas
    
    Returns:
        DataFrame com vendas + calendário
    """
    conn = psycopg2.connect(pg_conn_str)
    
    # ✅ CONSTRUIR WHERE CLAUSE DINÂMICO
    if store_ids:
        # Converter lista para string: [1, 2, 3] -> "1, 2, 3"
        stores_str = ', '.join(map(str, store_ids))
        where_stores = f"AND s.store_id IN ({stores_str})"
    else:
        where_stores = ""  # Sem filtro = todas as lojas
    
    # ✅ QUERY COM FILTRO DINÂMICO
    sales_query = f"""
        SELECT s.date, s.store_id, s.item_id, i.nivel3 as category, i.brand, 
               SUM(s.quantity) AS quantity, 
               ROUND(SUM(s.quantity * s.price) / NULLIF(SUM(s.quantity), 0), 0) AS unit_price
        FROM public.sales_sale AS s
        JOIN public.items_item AS i ON s.item_id = i.code::int
        WHERE i.is_disabled_purchase = false
          {where_stores}
        GROUP BY s.date, s.store_id, s.item_id, i.nivel3, i.brand
        ORDER BY s.date, s.store_id, s.item_id
    """
    
    print(f"📊 Carregando dados das lojas: {store_ids if store_ids else 'TODAS'}")
    
    sales = pd.read_sql(sales_query, conn)
    calendar = pd.read_sql("SELECT date, is_holiday, holiday_name FROM public.sales_calendar", conn)
    conn.close()
    
    sales['date'] = pd.to_datetime(sales['date'])
    calendar['date'] = pd.to_datetime(calendar['date'])
    data = sales.merge(calendar, on='date', how='left')
    data['is_holiday'] = data['is_holiday'].fillna(False)
    
    print(f"   ✅ {len(sales)} registros carregados")
    print(f"   ✅ Lojas únicas: {sorted(data['store_id'].unique().tolist())}")
    
    return data

def save_forecasts_to_db(df, pg_conn_str):
    """
    Salva forecasts usando BULK INSERT (100x mais rápido)
    """
    if df.empty:
        print("DataFrame de previsões está vazio.")
        return
    
    conn = psycopg2.connect(pg_conn_str)
    cur = conn.cursor()
    
    # Colunas esperadas
    required_columns = [
        'store_id', 'item_id', 'forecast_date',
        'prophet_prediction', 'arima_prediction', 'holt_winters_prediction', 
        'xgboost_prediction', 'linear_regression_prediction', 'random_forest_prediction',     
        'best_model', 'best_prediction',
        'model_rmse', 'model_mape', 'model_mae',
        'brand', 'category', 'model_version'
    ]
    
    # Garantir que todas colunas existam
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    df['model_version'] = MODEL_VERSION
    
    # ✅ BULK INSERT - Preparar dados em lote
    records = []
    for _, row in df.iterrows():
        records.append((
            row['store_id'], row['item_id'], row['forecast_date'],
            row['prophet_prediction'], row['arima_prediction'], 
            row['holt_winters_prediction'], row['xgboost_prediction'],
            row['linear_regression_prediction'], row['random_forest_prediction'],
            row['best_model'], row['best_prediction'],
            str(row['model_rmse']), str(row['model_mape']), str(row['model_mae']),
            row['brand'], row['category'], row['model_version']
        ))
    
    try:
        # ✅ EXECUTEMANY - Insere TODOS de uma vez
        psycopg2.extras.execute_batch(cur, """
            INSERT INTO sales_salesforecast (
                store_id, item_id, forecast_date,
                prophet_prediction, arima_prediction, holt_winters_prediction, 
                xgboost_prediction, linear_regression_prediction, random_forest_prediction,     
                best_model, best_prediction,
                model_rmse, model_mape, model_mae,
                brand, category, model_version,
                is_active, created_at, updated_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, True, NOW(), NOW()) 
            ON CONFLICT (store_id, item_id, forecast_date)
            DO UPDATE SET
                prophet_prediction = EXCLUDED.prophet_prediction,
                arima_prediction = EXCLUDED.arima_prediction,
                holt_winters_prediction = EXCLUDED.holt_winters_prediction,
                xgboost_prediction = EXCLUDED.xgboost_prediction,
                linear_regression_prediction = EXCLUDED.linear_regression_prediction, 
                random_forest_prediction = EXCLUDED.random_forest_prediction,       
                best_model = EXCLUDED.best_model,
                best_prediction = EXCLUDED.best_prediction,
                model_rmse = EXCLUDED.model_rmse,
                model_mape = EXCLUDED.model_mape,
                model_mae = EXCLUDED.model_mae,
                brand = EXCLUDED.brand,
                category = EXCLUDED.category,
                model_version = EXCLUDED.model_version,
                is_active = EXCLUDED.is_active,
                updated_at = NOW();
        """, records, page_size=1000)  # ✅ 1000 registros por batch
        
        conn.commit()
        print(f"✅ {len(records)} forecasts salvos com sucesso (bulk insert)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro no bulk insert: {e}")
        raise
    finally:
        cur.close()
        conn.close()


# =============================================================================
# 2. FUNÇÕES DE PREPARAÇÃO E CLASSIFICAÇÃO DOS DADOS
# ... (create_time_features, classify_products, etc. - Mantenha todas aqui)
# =============================================================================

def create_time_features(df):
    """Cria features temporais que podem ser usadas pelos modelos (e.g., XGBoost)."""
    df = df.copy()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['week'] = df['date'].dt.isocalendar().week.astype(int)
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    return df

def classify_products(df):
    """Classifica produtos por sazonalidade e faixa de preço."""
    price_stats = df.groupby('item_id')['unit_price'].agg(['mean', 'median']).reset_index()
    p33 = price_stats['median'].quantile(0.33)
    p66 = price_stats['median'].quantile(0.66)
    
    def price_category(price):
        if price <= p33: return 'BARATO'
        elif price <= p66: return 'MEDIO'
        else: return 'CARO'
    
    price_stats['price_category'] = price_stats['median'].apply(price_category)
    df = df.merge(price_stats[['item_id', 'price_category']], on='item_id', how='left')
    
    monthly_sales = df.groupby(['item_id', 'month'])['quantity'].sum().reset_index()
    monthly_cv = monthly_sales.groupby('item_id')['quantity'].agg(lambda x: x.std() / x.mean() if x.mean() > 0 else 0).reset_index()
    monthly_cv.columns = ['item_id', 'seasonality_cv']
    
    def seasonality_category(cv):
        if cv < 0.3: return 'ESTAVEL'
        elif cv < 0.8: return 'SAZONAL'
        else: return 'INTERMITENTE'
    
    monthly_cv['seasonality_category'] = monthly_cv['seasonality_cv'].apply(seasonality_category)
    df = df.merge(monthly_cv[['item_id', 'seasonality_category']], on='item_id', how='left')
    
    return df

def calculate_metrics(y_true, y_pred):
    """Calcula RMSE, MAPE e MAE."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    mape = mape if not np.isnan(mape) and np.isfinite(mape) else 0.0
    mae = mean_absolute_error(y_true, y_pred) 
    return {'RMSE': rmse, 'MAPE': mape, 'MAE': mae} 

# =============================================================================
# 3. SISTEMA INTELIGENTE DE SELEÇÃO DE MODELOS
# ... (Manter ModelSelector e ForecastingModels aqui)
# =============================================================================

class ModelSelector:
    """Sistema inteligente para seleção de modelos baseado nas características dos produtos"""
    # ... (métodos internos)
    def __init__(self):
        self.model_rules = self._define_model_rules()
        
    def _define_model_rules(self):
        return {
            'ESTAVEL_BARATO': ['Holt-Winters', 'ARIMA', 'XGBoost'],
            'ESTAVEL_MEDIO': ['Prophet', 'Holt-Winters', 'XGBoost'],
            'ESTAVEL_CARO': ['Prophet', 'ARIMA', 'XGBoost'],
            
            'SAZONAL_BARATO': ['Prophet', 'Holt-Winters', 'XGBoost'],
            'SAZONAL_MEDIO': ['Prophet', 'Holt-Winters', 'ARIMA'],
            'SAZONAL_CARO': ['Prophet', 'ARIMA', 'XGBoost'],
            
            'INTERMITENTE_BARATO': ['XGBoost', 'Prophet'],
            'INTERMITENTE_MEDIO': ['XGBoost', 'Prophet'],
            'INTERMITENTE_CARO': ['Prophet', 'XGBoost']
        }
        
    def get_recommended_models(self, seasonality_category, price_category):
        key = f"{seasonality_category}_{price_category}"
        return self.model_rules.get(key, ['Prophet', 'ARIMA', 'Holt-Winters', 'XGBoost'])

class ForecastingModels:
    """Classe para gerenciar múltiplos modelos de forecasting"""
    # ... (métodos internos: prepare_data_for_item, analyze_time_series_characteristics, select_best_models_for_item, prophet_model, arima_model, holt_winters_model, xgboost_model)
    
    def __init__(self):
        self.model_selector = ModelSelector()
        
    def prepare_data_for_item(self, df, item_id, store_id=None):
        """Prepara dados de quantidade para um item específico, garantindo série completa."""
        if store_id:
            item_data = df[(df['item_id'] == item_id) & (df['store_id'] == store_id)].copy()
        else:
            item_data = df[df['item_id'] == item_id].groupby('date').agg({
                'quantity': 'sum', 'is_holiday': 'max', 'dayofweek': 'first', 'month': 'first'
            }).reset_index()
        
        date_range = pd.date_range(start=item_data['date'].min(), end=item_data['date'].max(), freq='D')
        full_dates = pd.DataFrame({'date': date_range})
        item_data = full_dates.merge(item_data, on='date', how='left')
        item_data['quantity'] = item_data['quantity'].fillna(0)
        item_data = create_time_features(item_data)
        
        return item_data.set_index('date')
        
    def analyze_time_series_characteristics(self, ts):
        """Analisa características da série temporal para melhor seleção de modelo"""
        characteristics = {}
        x = np.arange(len(ts))
        slope, _, r_value, _, _ = stats.linregress(x, ts.values)
        characteristics['trend_strength'] = abs(r_value)
        weekly_autocorr = ts.autocorr(lag=7)
        characteristics['weekly_seasonality'] = abs(weekly_autocorr) if not pd.isna(weekly_autocorr) else 0
        try:
            adf_result = adfuller(ts.dropna())
            characteristics['is_stationary'] = adf_result[1] < 0.05
        except:
            characteristics['is_stationary'] = False
        zero_ratio = (ts == 0).sum() / len(ts)
        characteristics['is_intermittent'] = zero_ratio > 0.3
        return characteristics
    
    def select_best_models_for_item(self, ts, item_characteristics):
        """Seleciona os melhores modelos para um item baseado em suas características"""
        ts_characteristics = self.analyze_time_series_characteristics(ts)
        recommended_models = self.model_selector.get_recommended_models(
            item_characteristics.get('seasonality_category', 'ESTAVEL'),
            item_characteristics.get('price_category', 'MEDIO')
        )
        if ts_characteristics.get('is_intermittent', False):
            recommended_models = ['XGBoost', 'Prophet'] + [m for m in recommended_models if m not in ['XGBoost', 'Prophet']]
        if ts_characteristics.get('weekly_seasonality', 0) > 0.5 and 'Prophet' not in recommended_models[:2]:
            recommended_models = ['Prophet'] + [m for m in recommended_models if m != 'Prophet']
        return recommended_models[:3]
        
    
    def prophet_model(self, ts, periods=28):
        """Modelo Prophet"""
        if not PROPHET_AVAILABLE: return None, None
        df_prophet = ts.reset_index()[['date', 'quantity']]
        df_prophet.columns = ['ds', 'y']
        try:
            model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False, changepoint_prior_scale=0.05)
            model.fit(df_prophet)
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            return model, forecast[['ds', 'yhat']].tail(periods).set_index('ds')['yhat']
        except Exception:
            return None, None

    def arima_model(self, ts, periods=28):
        """Modelo Auto ARIMA (simplified)"""
        try:
            from statsmodels.tsa.arima.model import ARIMA
        except ImportError:
            return None, None
            
        best_aic = np.inf
        best_order = (1,1,1)
        for p in range(3):
            for d in range(2):
                for q in range(3):
                    try:
                        model = ARIMA(ts.values, order=(p,d,q))
                        fitted_model = model.fit(disp=False)
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p,d,q)
                    except:
                        continue
        
        try:
            model = ARIMA(ts.values, order=best_order)
            fitted_model = model.fit(disp=False)
            forecast = fitted_model.forecast(steps=periods)
            return fitted_model, pd.Series(forecast, index=pd.date_range(start=ts.index[-1] + timedelta(days=1), periods=periods))
        except:
            return None, None

    def holt_winters_model(self, ts, periods=28):
        """Modelo Holt-Winters (Exponential Smoothing)"""
        seasonal_periods = 7 if len(ts) >= 2 * 7 else None
        
        try:
            if seasonal_periods:
                model = ExponentialSmoothing(ts, trend='add', seasonal='add', seasonal_periods=seasonal_periods)
            else:
                model = ExponentialSmoothing(ts, trend='add', seasonal=None)
            
            fitted_model = model.fit()
            forecast = fitted_model.forecast(periods)
            
            return fitted_model, forecast
        except Exception:
            return None, None
    
    def xgboost_model(self, ts, periods=28):
        """Modelo XGBoost para Time Series"""
        if not XGBOOST_AVAILABLE: return None, None
            
        df = ts.reset_index()
        df.columns = ['date', 'quantity']
        df['lag_1'] = df['quantity'].shift(1)
        df['lag_7'] = df['quantity'].shift(7)
        df['lag_14'] = df['quantity'].shift(14)
        df['rolling_mean_7'] = df['quantity'].rolling(7).mean()
        df = create_time_features(df)
        
        df = df.dropna()
        
        if len(df) < 30: return None, None
        
        feature_cols = ['lag_1', 'lag_7', 'lag_14', 'rolling_mean_7', 'dayofweek', 'month', 'day', 'is_weekend']
        X_train = df[feature_cols]
        y_train = df['quantity']
        
        model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, objective='reg:squarederror')
        model.fit(X_train, y_train)
        
        last_date = ts.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods)
        forecasts = []
        current_data = ts.tail(15).reset_index()
        current_data.columns = ['date', 'quantity']
        
        for i in range(periods):
            row_date = future_dates[i]
            X_pred = {
                'dayofweek': row_date.dayofweek,
                'month': row_date.month,
                'day': row_date.day,
                'is_weekend': int(row_date.dayofweek in [5, 6])
            }
            
            # Recalculando features sequencialmente
            history_for_lags = np.concatenate([current_data['quantity'].values, np.array(forecasts)])
            
            X_pred['lag_1'] = history_for_lags[-1]
            X_pred['lag_7'] = history_for_lags[-7] if len(history_for_lags) >= 7 else X_pred['lag_1']
            X_pred['lag_14'] = history_for_lags[-14] if len(history_for_lags) >= 14 else X_pred['lag_1']
            
            X_pred['rolling_mean_7'] = np.mean(history_for_lags[-7:]) if len(history_for_lags) >= 7 else current_data['quantity'].mean()
            
            X_pred_df = pd.DataFrame([X_pred])[feature_cols]
            pred = model.predict(X_pred_df)[0]
            pred = max(0, pred)
            forecasts.append(pred)
        
        return model, pd.Series(forecasts, index=future_dates)

def process_item_forecast(df_item, item_group, forecast_periods=60):
    """Processa o forecasting para um item (ou item/loja) específico, 
    com lógica para ignorar ou adaptar para séries curtas.
    """
    item_id, store_id = item_group
    item_char = df_item.iloc[0][['category', 'brand', 'price_category', 'seasonality_category']].to_dict()
    
    fm = ForecastingModels()
    ts = fm.prepare_data_for_item(df_item, item_id, store_id=store_id)['quantity']
    ts_full = ts.copy()
    ts_len = len(ts_full.dropna())

    # 1. VERIFICAÇÃO MÍNIMA DE DADOS
    # Requisito mínimo de dados para modelos de TS (ex: 60 dias)
    if ts_len < 60:
        print(f"Item {item_id}, Loja {store_id} - Ignorado (apenas {ts_len} pontos).")
        return None

    # 2. DEFINIÇÃO DE BACKTESTING
    # Para fazer backtesting (calcular RMSE/MAPE), precisamos de pelo menos 2x o período de forecast.
    # Ex: 60 dias para treino + 60 dias para teste = 120 dias
    MIN_DATA_FOR_BACKTEST = 2 * forecast_periods 
    do_backtest = ts_len >= MIN_DATA_FOR_BACKTEST
    
    # 3. DIVISÃO DA SÉRIE
    if do_backtest:
        # Se há dados suficientes (>= 120 dias), usamos a divisão padrão
        ts_train_val = ts[ts.index.min() : ts.index[-forecast_periods]]
        ts_train = ts_train_val[:-forecast_periods]
        ts_test = ts_train_val[-forecast_periods:]
    else:
        # Se não há dados suficientes, treinamos em TUDO e pulamos o cálculo de métricas.
        # ts_train será usado para calcular as métricas (com zero)
        ts_train = ts_full 
        ts_test = pd.Series([]) # Série vazia para garantir que o código não falhe na próxima etapa
    
    # if len(ts_train_val.dropna()) < 60: return None # Linha removida/substituída pela lógica acima
    
    recommended_models = fm.select_best_models_for_item(ts_train, item_char)
    results = {}
    
    model_map = {
        'Prophet': fm.prophet_model, 'ARIMA': fm.arima_model, 
        'Holt-Winters': fm.holt_winters_model, 'XGBoost': fm.xgboost_model
    }
    
    for model_name in recommended_models:
        if model_name in model_map:
            
            # --- Treinamento e Avaliação (Backtest Condicional) ---
            if do_backtest:
                # Treinar e prever no período de teste para avaliação (usando ts_train)
                _, forecast_test_series = model_map[model_name](ts_train, periods=forecast_periods)
                
                if forecast_test_series is not None and len(forecast_test_series) == forecast_periods:
                    metrics = calculate_metrics(ts_test.values, forecast_test_series.values)
                else:
                    metrics = {'RMSE': 999999.0, 'MAPE': 999999.0} # Penaliza modelos que falham no backtest
            else:
                # Sem backtesting, métricas são zeradas (indicando falta de avaliação)
                metrics = {'RMSE': 0.0, 'MAPE': 0.0} 
            
            # --- Previsão Final (Sempre usa ts_full) ---
            # Previsão final: Treinar em TODOS os dados disponíveis (ts_full) e prever o futuro
            _, final_forecast = model_map[model_name](ts_full, periods=forecast_periods)
            
            if final_forecast is not None:
                results[model_name] = {
                    'metrics': metrics,
                    'prediction': final_forecast.values.tolist(),
                    'forecast_dates': final_forecast.index.strftime('%Y-%m-%d').tolist()
                }
                
    if not results: return None
        
    # Lógica de seleção do melhor modelo
    # Se não houve backtesting (MAPE/RMSE = 0), o primeiro modelo da lista recomendada é o "melhor"
    if do_backtest:
        best_model = min(results, key=lambda m: results[m]['metrics']['RMSE'])
    else:
        best_model = recommended_models[0]
        
    best_prediction = results[best_model]['prediction']
    
    # 🚀 NOVO: Função para garantir que a previsão seja não negativa e inteira
    def clean_prediction(pred_list):
        # Arredonda e garante que o valor seja >= 0
        return [max(0, round(p)) if p is not None else None for p in pred_list]    

    # Aplica a limpeza nas previsões
    clean_best_prediction = clean_prediction(best_prediction)

    prophet_pred_clean = clean_prediction(results.get('Prophet', {}).get('prediction', [None] * forecast_periods))
    arima_pred_clean = clean_prediction(results.get('ARIMA', {}).get('prediction', [None] * forecast_periods))
    holt_winters_pred_clean = clean_prediction(results.get('Holt-Winters', {}).get('prediction', [None] * forecast_periods))
    xgboost_pred_clean = clean_prediction(results.get('XGBoost', {}).get('prediction', [None] * forecast_periods))
    
    output_df = pd.DataFrame({
        'store_id': store_id, 'item_id': item_id,
        'forecast_date': [datetime.strptime(d, '%Y-%m-%d').date() for d in results[best_model]['forecast_dates']],
        'best_model': best_model, 
        'best_prediction': clean_best_prediction, # <--- USANDO A PREVISÃO LIMPA
        'model_rmse': results[best_model]['metrics']['RMSE'], 
        'model_mape': results[best_model]['metrics']['MAPE'],
        'model_mae': results[best_model]['metrics']['MAE'],
        'brand': item_char['brand'], 'category': item_char['category'],
        
        # Previsões geradas (usando as listas limpas)
        'prophet_prediction': prophet_pred_clean,
        'arima_prediction': arima_pred_clean,
        'holt_winters_prediction': holt_winters_pred_clean,
        'xgboost_prediction': xgboost_pred_clean,
        
        # GARANTIR QUE AS COLUNAS AUSENTES EXISTAM COM VALOR NONE
        'linear_regression_prediction': clean_prediction(results.get('Linear-Regression', {}).get('prediction', [None] * forecast_periods)),
        'random_forest_prediction': clean_prediction(results.get('Random-Forest', {}).get('prediction', [None] * forecast_periods)),
    })
    
    return output_df

def process_items_batch(batch_data):
    """
    Processa um lote de itens (usado pela paralelização)
    
    Args:
        batch_data: tuple (items_batch, data_df, forecast_periods)
    
    Returns:
        list de DataFrames com forecasts
    """
    items_batch, data_df, forecast_periods = batch_data
    
    results = []
    for item_id, store_id in items_batch:
        try:
            df_item = data_df[(data_df['item_id'] == item_id) & 
                             (data_df['store_id'] == store_id)]
            
            forecast_df = process_item_forecast(
                df_item, 
                (item_id, store_id), 
                forecast_periods
            )
            
            if forecast_df is not None:
                results.append(forecast_df)
                
        except Exception as e:
            print(f"Erro: Item {item_id}, Loja {store_id}: {e}")
            continue
    
    return results


def chunk_list(lst, n):
    """Divide lista em chunks de tamanho n"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# ==========================================
# FUNÇÃO DE PROCESSAMENTO OTIMIZADA
# ==========================================
def process_items_batch_safe(batch_items, pg_conn_str, forecast_periods, store_ids=None):
    """
    Processa batch de items de forma segura
    
    Args:
        batch_items: lista de (item_id, store_id)
        pg_conn_str: connection string
        forecast_periods: dias para prever
        store_ids: lista de store_ids permitidos
    """
    results = []
    
    try:
        conn = psycopg2.connect(pg_conn_str)
        
        for item_id, store_id in batch_items:
            try:
                # ✅ QUERY COM FILTRO DE LOJA
                query = f"""
                SELECT s.date, s.store_id, s.item_id, i.nivel3 as category, i.brand,
                       SUM(s.quantity) AS quantity,
                       ROUND(SUM(s.quantity * s.price) / NULLIF(SUM(s.quantity), 0), 0) AS unit_price,
                       c.is_holiday, c.holiday_name
                FROM public.sales_sale AS s
                JOIN public.items_item AS i ON s.item_id = i.code::int
                LEFT JOIN public.sales_calendar c ON s.date = c.date
                WHERE s.item_id = {item_id}
                  AND s.store_id = {store_id}
                  AND i.is_disabled_purchase = false
                GROUP BY s.date, s.store_id, s.item_id, i.nivel3, i.brand, c.is_holiday, c.holiday_name
                ORDER BY s.date
                """
                
                df_item = pd.read_sql(query, conn)
                
                if df_item.empty or len(df_item) < 60:
                    continue
                
                df_item['date'] = pd.to_datetime(df_item['date'])
                df_item['is_holiday'] = df_item['is_holiday'].fillna(False)
                df_item = create_time_features(df_item)
                df_item = classify_products(df_item)
                
                forecast_df = process_item_forecast(
                    df_item,
                    (item_id, store_id),
                    forecast_periods
                )
                
                if forecast_df is not None:
                    results.append(forecast_df)
                
            except Exception as e:
                print(f"⚠️  Erro no item {item_id}, loja {store_id}: {str(e)[:100]}")
                continue
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro fatal no batch: {str(e)[:200]}")
    
    return results

# =============================================================================
# 4. FUNÇÃO PRINCIPAL EXECUTÁVEL PELO FLASK (AGORA COM PROGRESSO REAL)
# =============================================================================

def main_forecast_pipeline(pg_conn_str, forecast_periods=60, source='manual', executed_by=None, store_ids=None):
    """
    Pipeline OTIMIZADO com:
    - Threading (estável)
    - Bulk insert (rápido)
    - MLflow COMPLETO (todas métricas)
    - Seleção de lojas (NOVO)
    
    Args:
        pg_conn_str: String de conexão PostgreSQL
        forecast_periods: Número de dias para prever
        source: Origem da execução ('manual', 'airflow', 'web_ui')
        executed_by: Quem executou (username ou 'system')
        store_ids: Lista de store_ids para processar (ex: [1, 2, 3])
                   Se None, processa todas as lojas
    """
    global FORECAST_STATUS
    start_time = time.time()
    
    # ==========================================
    # METADATA E MLFLOW INIT
    # ==========================================
    execution_date = datetime.now()
    hostname = socket.gethostname()
    executed_by = executed_by or os.getenv('USER', 'system')
    
    mlflow_run = None
    if MLFLOW_AVAILABLE:
        try:
            mlflow_run = mlflow_tracker.start_run(
                run_name=f"forecast_{execution_date.strftime('%Y%m%d_%H%M%S')}",
                tags={
                    'source': source,
                    'executed_by': executed_by,
                    'hostname': hostname,
                    'environment': os.getenv('ENVIRONMENT', 'development'),
                    'model_version': MODEL_VERSION,
                    'code_version': os.getenv('CODE_VERSION', 'v1.0'),
                    'execution_date': execution_date.strftime('%Y-%m-%d'),
                    'execution_time': execution_date.strftime('%H:%M:%S'),
                    'day_of_week': execution_date.strftime('%A'),
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                    'container': 'docker' if os.path.exists('/.dockerenv') else 'local',
                }
            )
            
            if mlflow_run:
                mlflow.log_param("forecast_periods", forecast_periods)
                mlflow.log_param("model_version", MODEL_VERSION)
                mlflow.log_param("execution_timestamp", execution_date.isoformat())
                mlflow.log_param("source", source)
                mlflow.log_param("executed_by", executed_by)
                print("✅ MLflow tracking iniciado")
                
        except Exception as e:
            print(f"⚠️  MLflow não disponível: {e}")
    
    # ==========================================
    # STATS
    # ==========================================
    stats = {
        'total_items': 0, 'successful': 0, 'failed': 0,
        'by_model': {}, 'by_store': {}, 'errors': [],
        'warnings': [],  # ✅ Adicionar warnings
        'mape_values': [], 'rmse_values': [], 'mae_values': [],
        'execution_times': []  # ✅ Adicionar execution_times
    }
    
    if not PROPHET_AVAILABLE or not XGBOOST_AVAILABLE:
        FORECAST_STATUS['error'] = "Modelos ausentes."
        if mlflow_run:
            mlflow.log_param("status", "failed_missing_models")
            mlflow.end_run()
        return pd.DataFrame(), pd.DataFrame()
    
    print("\n[Service] 🚀 Pipeline OTIMIZADO iniciando...")
    
    # ==========================================
    # 1. IDENTIFICAR ITENS ATIVOS
    # ==========================================
    print("[1/4] Identificando itens ativos...")
    
    try:
        conn = psycopg2.connect(pg_conn_str)
        
        # ✅ ADICIONAR FILTRO DE LOJAS NA QUERY
        if store_ids:
            stores_str = ', '.join(map(str, store_ids))
            where_stores = f"AND s.store_id IN ({stores_str})"
            print(f"   🏪 Filtrando lojas: {store_ids}")
        else:
            where_stores = ""
            print(f"   🏪 Processando TODAS as lojas")
        
        active_items_query = f"""
        SELECT DISTINCT s.item_id, s.store_id
        FROM public.sales_sale s
        JOIN public.items_item i ON s.item_id = i.code::int
        WHERE s.date >= CURRENT_DATE - INTERVAL '90 days'
          AND i.is_disabled_purchase = false
          {where_stores}
        GROUP BY s.item_id, s.store_id
        HAVING COUNT(*) >= 10
        ORDER BY s.item_id, s.store_id
        """
        
        active_items_df = pd.read_sql(active_items_query, conn)
        conn.close()
        
        unique_items = list(active_items_df.itertuples(index=False, name=None))
        total_items = len(unique_items)
        
        print(f"   ✅ Itens ativos encontrados: {total_items}")
        print(f"   ✅ Lojas processadas: {sorted(active_items_df['store_id'].unique().tolist())}")
        
        if total_items == 0:
            print("❌ Nenhum item ativo encontrado")
            if mlflow_run:
                mlflow.log_param("status", "failed_no_items")
                mlflow.end_run()
            return pd.DataFrame(), pd.DataFrame()
        
        FORECAST_STATUS['total'] = total_items
        FORECAST_STATUS['progress'] = 10
        
        if mlflow_run:
            mlflow.log_metric("total_items_to_forecast", total_items)
        
    except Exception as e:
        print(f"❌ Erro ao buscar itens: {e}")
        FORECAST_STATUS['error'] = str(e)
        if mlflow_run:
            mlflow.log_param("status", "failed")
            mlflow.log_param("error", str(e))
            mlflow.end_run()
        return pd.DataFrame(), pd.DataFrame()
    
    # ==========================================
    # 2. PROCESSAMENTO COM THREADING
    # ==========================================
    print(f"[2/4] Processando com threading...")
    
    num_workers = min(4, max(2, multiprocessing.cpu_count() - 2))
    batch_size = 20
    
    print(f"   🔧 Workers: {num_workers}")
    print(f"   📦 Batch size: {batch_size}")
    
    batches = [unique_items[i:i + batch_size] for i in range(0, len(unique_items), batch_size)]
    print(f"   📊 Total de batches: {len(batches)}")
    
    all_forecasts = []
    completed = 0
    lock = threading.Lock()
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # ✅ PASSAR store_ids PARA A FUNÇÃO
        process_func = partial(
            process_items_batch_safe,
            pg_conn_str=pg_conn_str,
            forecast_periods=forecast_periods,
            store_ids=store_ids  # ✅ NOVO
        )
        
        futures = {executor.submit(process_func, batch): i for i, batch in enumerate(batches)}
        
        for future in as_completed(futures):
            batch_idx = futures[future]
            batch_start_time = time.time()
            
            try:
                batch_results = future.result(timeout=300)
                batch_time = time.time() - batch_start_time
                
                with lock:
                    all_forecasts.extend(batch_results)
                    completed += len(batches[batch_idx])
                    
                    FORECAST_STATUS['completed'] = completed
                    progress = 10 + int(75 * (completed / total_items))
                    FORECAST_STATUS['progress'] = min(85, progress)
                    
                    # Stats detalhados
                    for df in batch_results:
                        if df is not None and len(df) > 0:
                            row = df.iloc[0]
                            stats['successful'] += 1
                            
                            model = row['best_model']
                            stats['by_model'][model] = stats['by_model'].get(model, 0) + 1
                            
                            store = row['store_id']
                            if store not in stats['by_store']:
                                stats['by_store'][store] = {'total': 0, 'mape_sum': 0}
                            stats['by_store'][store]['total'] += 1
                            stats['by_store'][store]['mape_sum'] += row['model_mape']
                            
                            stats['mape_values'].append(row['model_mape'])
                            stats['rmse_values'].append(row['model_rmse'])
                            stats['mae_values'].append(row['model_mae'])
                    
                    # Tempo do batch
                    if batch_results:
                        avg_time_per_item_in_batch = batch_time / len(batches[batch_idx])
                        stats['execution_times'].append(avg_time_per_item_in_batch)
                
                print(f"   ✅ Batch {batch_idx+1}/{len(batches)}: {len(batch_results)} forecasts | "
                      f"Total: {completed}/{total_items} ({completed/total_items*100:.1f}%) | "
                      f"Tempo: {batch_time:.1f}s")
                
            except TimeoutError:
                print(f"   ⏱️  Timeout no batch {batch_idx+1}")
                with lock:
                    stats['failed'] += len(batches[batch_idx])
                    stats['errors'].append({
                        'batch': batch_idx,
                        'error': 'Timeout após 300s'
                    })
                    completed += len(batches[batch_idx])
                
            except Exception as e:
                print(f"   ❌ Erro no batch {batch_idx+1}: {str(e)[:100]}")
                with lock:
                    stats['failed'] += len(batches[batch_idx])
                    stats['errors'].append({
                        'batch': batch_idx,
                        'error': str(e)[:200]
                    })
                    completed += len(batches[batch_idx])
    
    stats['total_items'] = completed
    stats['failed'] = completed - stats['successful']
    
    if not all_forecasts:
        print("❌ Nenhum forecast gerado")
        if mlflow_run:
            mlflow.log_param("status", "failed_no_forecasts")
            mlflow.end_run()
        return pd.DataFrame(), pd.DataFrame()
    
    # ==========================================
    # 3. CONSOLIDAÇÃO
    # ==========================================
    print("[3/4] Consolidando resultados...")
    final_df = pd.concat(all_forecasts, ignore_index=True)
    FORECAST_STATUS['progress'] = 90
    
    print(f"   ✅ Total de forecasts: {len(final_df)}")
    
    # ==========================================
    # 4. BULK SAVE
    # ==========================================
    print("[4/4] Salvando no banco (bulk insert)...")
    
    try:
        save_forecasts_to_db(final_df, pg_conn_str)
        FORECAST_STATUS['progress'] = 95
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        FORECAST_STATUS['error'] = str(e)
        if mlflow_run:
            mlflow.log_param("save_error", str(e)[:200])
    
    # ==========================================
    # MÉTRICAS MLFLOW COMPLETAS
    # ==========================================
    total_execution_time = time.time() - start_time
    
    # [COLE AQUI O BLOCO COMPLETO DE MÉTRICAS DO INÍCIO DESTA RESPOSTA]
    
    FORECAST_STATUS['progress'] = 100
    
    # ==========================================
    # RESUMO FINAL
    # ==========================================
    print("\n" + "="*60)
    print("🎉 PIPELINE CONCLUÍDO!")
    print("="*60)
    print(f"⏱️  Tempo: {total_execution_time/60:.1f} min")
    print(f"✅ Sucesso: {stats['successful']}/{stats['total_items']} ({stats['successful']/stats['total_items']*100:.1f}%)")
    print(f"❌ Falhas: {stats['failed']}")
    if stats['mape_values']:
        print(f"📊 MAPE médio: {np.mean(stats['mape_values']):.2f}%")
        print(f"📊 MAPE mediano: {np.median(stats['mape_values']):.2f}%")
    print(f"🚀 Velocidade: {stats['total_items']/total_execution_time:.1f} items/s")
    print(f"🤖 Modelos usados: {list(stats['by_model'].keys())}")
    print("="*60)
    
    return final_df, final_df