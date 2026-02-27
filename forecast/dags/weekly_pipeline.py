# dags/weekly_pipeline.py
"""
DAG do Airflow que automatiza TODO o processo semanal
Usa as mesmas funções do Flask, garantindo consistência
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, '/app')  # Path dentro do container Docker

from app.transfer import (
    transfer_bi_productos,
    transfer_orders,
    transfer_stock,
    transfer_sales
)
from app.forecasting_service import main_forecast_pipeline, save_forecasts_to_db
from app.utils.performance_tracker import (
    compare_forecast_vs_actual,
    detect_model_drift,
    create_performance_table
)
from app.config import Config
import logging
import mlflow

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email': ['data-team@empresa.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'weekly_forecast_pipeline',
    default_args=default_args,
    description='Pipeline semanal automatizado de forecasting',
    schedule_interval='0 2 * * 1',  # Segunda-feira 2 AM
    catchup=False,
    max_active_runs=1,
    tags=['forecast', 'sales', 'weekly', 'automated']
)

# ===== TASK 1: Transferir TODAS as Tabelas =====
def task_transfer_all_tables(**context):
    """Executa todas as transferências em sequência"""
    logger.info("Iniciando transferência de todas as tabelas...")
    
    results = {}
    
    # 1. Produtos
    logger.info("Transferindo produtos...")
    results['produtos'] = transfer_bi_productos(
        Config.SQLSERVER_CONNECTION_STRING,
        Config.POSTGRES_CONNECTION_STRING
    )
    
    # 2. Ordens
    logger.info("Transferindo ordens de compra...")
    results['orders'] = transfer_orders(
        Config.SQLSERVER_CONNECTION_STRING,
        Config.POSTGRES_CONNECTION_STRING
    )
    
    # 3. Estoque
    logger.info("Transferindo estoque...")
    results['stock'] = transfer_stock(
        Config.SQLSERVER_CONNECTION_STRING,
        Config.POSTGRES_CONNECTION_STRING
    )
    
    # 4. Vendas
    logger.info("Transferindo vendas...")
    results['sales'] = transfer_sales(
        Config.SQLSERVER_CONNECTION_STRING,
        Config.POSTGRES_CONNECTION_STRING
    )
    
    logger.info(f"✅ Todas as transferências concluídas: {results}")
    return results

transfer_task = PythonOperator(
    task_id='transfer_all_tables',
    python_callable=task_transfer_all_tables,
    dag=dag,
)

# ===== TASK 2: Gerar Forecast com MLflow =====
def task_generate_forecast(**context):
    """Executa forecast com tracking do MLflow"""
    logger.info("Iniciando geração de forecast...")
    
    # Configurar tag para indicar que veio do Airflow
    mlflow.set_tracking_uri(getattr(Config, 'MLFLOW_TRACKING_URI', 'http://mlflow:5000'))
    
    with mlflow.start_run(run_name=f"airflow_weekly_{context['ds']}", tags={'source': 'airflow'}):
        mlflow.log_param("execution_date", context['ds'])
        mlflow.log_param("dag_run_id", context['run_id'])
        
        forecast_df, _ = main_forecast_pipeline(
            Config.POSTGRES_CONNECTION_STRING,
            forecast_periods=60
        )
        
        total_forecasts = len(forecast_df)
        logger.info(f"✅ Forecast gerado: {total_forecasts} previsões")
        
        # Salvar no banco
        save_forecasts_to_db(forecast_df, Config.POSTGRES_CONNECTION_STRING)
        
        context['ti'].xcom_push(key='total_forecasts', value=total_forecasts)
        
        return total_forecasts

forecast_task = PythonOperator(
    task_id='generate_forecast',
    python_callable=task_generate_forecast,
    dag=dag,
)

# ===== TASK 3: Comparar com Real (Semana Passada) =====
def task_compare_performance(**context):
    """Compara previsões da semana passada com vendas reais"""
    logger.info("Comparando forecast vs vendas reais...")
    
    # Criar tabela se não existir
    create_performance_table(Config.POSTGRES_CONNECTION_STRING)
    
    # Comparar últimos 7 dias
    date_end = datetime.strptime(context['ds'], '%Y-%m-%d').date() - timedelta(days=1)
    
    total_mape = 0
    days_checked = 0
    
    for days_ago in range(7):
        date_to_check = date_end - timedelta(days=days_ago)
        
        df = compare_forecast_vs_actual(
            Config.POSTGRES_CONNECTION_STRING,
            date_to_check
        )
        
        if not df.empty:
            total_mape += df['mape'].mean()
            days_checked += 1
    
    if days_checked > 0:
        avg_mape = total_mape / days_checked
        logger.info(f"📊 MAPE médio (última semana): {avg_mape:.2f}%")
        context['ti'].xcom_push(key='weekly_mape', value=avg_mape)
        return avg_mape
    else:
        logger.warning("⚠️ Sem dados reais para comparar ainda")
        return None

compare_task = PythonOperator(
    task_id='compare_with_actual',
    python_callable=task_compare_performance,
    dag=dag,
)

# ===== TASK 4: Detectar Drift =====
def task_detect_drift(**context):
    """Verifica se modelo está degradando"""
    logger.info("Verificando drift do modelo...")
    
    has_drift = detect_model_drift(Config.POSTGRES_CONNECTION_STRING, lookback_days=60)
    
    context['ti'].xcom_push(key='has_drift', value=has_drift)
    
    if has_drift:
        logger.warning("🔴 DRIFT DETECTADO! Considerar retreinamento.")
        # Aqui você pode adicionar lógica para trigger de retreinamento
    else:
        logger.info("✅ Modelo estável")
    
    return has_drift

drift_task = PythonOperator(
    task_id='detect_drift',
    python_callable=task_detect_drift,
    dag=dag,
)

# ===== TASK 5: Enviar Relatório =====
def task_send_report(**context):
    """Gera relatório final"""
    ti = context['ti']
    
    total_forecasts = ti.xcom_pull(key='total_forecasts', task_ids='generate_forecast')
    weekly_mape = ti.xcom_pull(key='weekly_mape', task_ids='compare_with_actual')
    has_drift = ti.xcom_pull(key='has_drift', task_ids='detect_drift')
    
    report = f"""
    ✅ Pipeline Semanal Concluído - {context['ds']}
    
    📊 Resultados:
    - Previsões geradas: {total_forecasts}
    - MAPE médio (última semana): {weekly_mape:.2f}% {'⚠️' if weekly_mape and weekly_mape > 25 else '✅'}
    - Status do Modelo: {'🔴 DRIFT DETECTADO' if has_drift else '✅ Estável'}
    
    🔗 MLflow: http://localhost:5000
    🔗 Airflow: http://localhost:8080
    🔗 Dashboard: http://localhost:5001/dashboard
    
    ---
    Executado automaticamente pelo Airflow
    """
    
    logger.info(report)
    
    # Aqui você pode adicionar envio de email
    # from airflow.providers.email.operators.email import EmailOperator
    
    return report

report_task = PythonOperator(
    task_id='send_report',
    python_callable=task_send_report,
    dag=dag,
)

# ===== DEFINIR ORDEM =====
transfer_task >> forecast_task >> compare_task >> drift_task >> report_task