# app/utils/mlflow_wrapper.py (VERSÃO ROBUSTA)
import mlflow
import mlflow.sklearn
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MLflowTracker:
    """Classe para gerenciar logging no MLflow"""
    
    def __init__(self):
        self._initialized = False
        self._tracking_uri = None
        
        try:
            from app.config import Config
            self._tracking_uri = Config.MLFLOW_TRACKING_URI
            mlflow.set_tracking_uri(self._tracking_uri)
            
            # NÃO criar experimento na inicialização!
            # Vai criar sob demanda quando precisar
            self._initialized = True
            logger.info(f"✅ MLflow configurado: {self._tracking_uri}")
            
        except Exception as e:
            logger.warning(f"⚠️  MLflow não disponível na inicialização: {e}")
            logger.warning(f"   O sistema vai tentar conectar quando necessário.")
    
    def _ensure_experiment(self, experiment_name="paraguay_supermarket_forecast"):
        """Garante que o experimento existe (cria sob demanda)"""
        if not self._initialized:
            return False
            
        try:
            # Tentar criar/obter experimento
            mlflow.set_experiment(experiment_name)
            return True
        except Exception as e:
            logger.warning(f"Erro ao configurar experimento MLflow: {e}")
            return False
    
    def start_run(self, run_name=None, tags=None):
        """Inicia uma run do MLflow"""
        if not self._initialized:
            logger.warning("MLflow não inicializado, pulando tracking")
            return None
            
        try:
            # Garantir que experimento existe
            if not self._ensure_experiment():
                return None
            
            if run_name is None:
                run_name = f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            tags = tags or {}
            tags['source'] = tags.get('source', 'manual')
            
            return mlflow.start_run(run_name=run_name, tags=tags)
            
        except Exception as e:
            logger.warning(f"Erro ao iniciar run MLflow: {e}")
            return None
    
    def log_metric_safe(self, key, value):
        """Loga métrica com tratamento de erro"""
        if not self._initialized:
            return
            
        try:
            if value is not None and not isinstance(value, str):
                mlflow.log_metric(key, float(value))
        except Exception as e:
            logger.warning(f"Erro ao logar métrica {key}: {e}")
    
    def log_param_safe(self, key, value):
        """Loga parâmetro com tratamento de erro"""
        if not self._initialized:
            return
            
        try:
            if value is not None:
                mlflow.log_param(key, str(value))
        except Exception as e:
            logger.warning(f"Erro ao logar parâmetro {key}: {e}")
    
    def log_item_metrics(self, item_id, store_id, model_name, rmse, mape, mae):
        """Loga métricas de um item específico (nested run)"""
        if not self._initialized:
            return
            
        try:
            with mlflow.start_run(nested=True, run_name=f"item_{item_id}_store_{store_id}"):
                mlflow.log_param("item_id", item_id)
                mlflow.log_param("store_id", store_id)
                mlflow.log_param("best_model", model_name)
                mlflow.log_metric("RMSE", float(rmse))
                mlflow.log_metric("MAPE", float(mape))
                mlflow.log_metric("MAE", float(mae))
        except Exception as e:
            logger.warning(f"Erro ao logar métricas do item {item_id}: {e}")

# Instância global - não falha se MLflow indisponível
mlflow_tracker = MLflowTracker()