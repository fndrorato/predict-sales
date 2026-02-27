# app/utils/performance_tracker.py
"""
Compara previsões com vendas reais e detecta drift
"""
import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_performance_table(pg_conn_str):
    """Cria tabela para armazenar performance real vs previsto"""
    conn = psycopg2.connect(pg_conn_str)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales_forecast_performance (
            id SERIAL PRIMARY KEY,
            store_id INTEGER,
            item_id BIGINT,
            forecast_date DATE,
            predicted_quantity NUMERIC,
            actual_quantity NUMERIC,
            error NUMERIC,
            abs_error NUMERIC,
            mape NUMERIC,
            model_used VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    # Índice para consultas rápidas
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_performance_date 
        ON sales_forecast_performance(forecast_date);
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Tabela sales_forecast_performance criada/verificada")

def compare_forecast_vs_actual(pg_conn_str, date_to_check):
    """Compara previsões com vendas reais para uma data específica"""
    conn = psycopg2.connect(pg_conn_str)
    
    query = """
    SELECT 
        f.store_id,
        f.item_id,
        f.forecast_date,
        f.best_prediction as predicted,
        COALESCE(SUM(s.quantity), 0) as actual,
        f.best_model
    FROM sales_salesforecast f
    LEFT JOIN sales_sale s 
        ON f.store_id = s.store_id 
        AND f.item_id = s.item_id 
        AND f.forecast_date = s.date
    WHERE f.forecast_date = %s
    GROUP BY f.store_id, f.item_id, f.forecast_date, f.best_prediction, f.best_model
    """
    
    df = pd.read_sql(query, conn, params=(date_to_check,))
    
    if df.empty:
        logger.warning(f"Sem dados para comparar na data {date_to_check}")
        conn.close()
        return pd.DataFrame()
    
    # Calcular métricas
    df['error'] = df['actual'] - df['predicted']
    df['abs_error'] = df['error'].abs()
    df['mape'] = np.where(df['actual'] > 0, df['abs_error'] / df['actual'] * 100, 0)
    
    # Salvar na tabela de performance
    df[['store_id', 'item_id', 'forecast_date', 'predicted', 'actual', 
        'error', 'abs_error', 'mape', 'best_model']].to_sql(
        'sales_forecast_performance',
        conn,
        if_exists='append',
        index=False,
        method='multi'
    )
    
    conn.close()
    
    avg_mape = df['mape'].mean()
    logger.info(f"Comparação concluída. MAPE médio: {avg_mape:.2f}%")
    
    return df

def detect_model_drift(pg_conn_str, lookback_days=60):
    """Detecta se há degradação na performance do modelo"""
    conn = psycopg2.connect(pg_conn_str)
    
    query = """
    SELECT 
        DATE_TRUNC('week', forecast_date) as week,
        AVG(mape) as avg_mape,
        AVG(abs_error) as avg_abs_error,
        COUNT(*) as predictions
    FROM sales_forecast_performance
    WHERE forecast_date >= CURRENT_DATE - INTERVAL '%s days'
    GROUP BY week
    HAVING COUNT(*) > 10
    ORDER BY week
    """
    
    df = pd.read_sql(query, conn, params=(lookback_days,))
    conn.close()
    
    if len(df) < 3:
        logger.warning("Dados insuficientes para detectar drift")
        return False
    
    # Comparar últimas 2 semanas vs primeiras 2 semanas
    recent_mape = df.tail(2)['avg_mape'].mean()
    older_mape = df.head(2)['avg_mape'].mean()
    
    drift_threshold = 1.3  # 30% de piora
    
    if recent_mape > older_mape * drift_threshold:
        logger.warning(f"🔴 DRIFT DETECTADO! MAPE aumentou de {older_mape:.2f}% para {recent_mape:.2f}%")
        return True
    
    logger.info(f"✅ Modelo estável. MAPE: {older_mape:.2f}% → {recent_mape:.2f}%")
    return False