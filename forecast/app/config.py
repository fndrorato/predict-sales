import os


class Config:
    SQLSERVER_CONNECTION_STRING = (
        "DRIVER={FreeTDS};SERVER=192.168.30.8;PORT=1402;DATABASE=pegasus;"
        "UID=consulta;PWD=123consulta;TDS_Version=7.1;"
    )

    POSTGRES_CONNECTION_STRING = (
        "host=host.docker.internal dbname=boxmayorista user=boxuser password=1234"
    )
    
    LOCAL_POSTGRES_CONNECTION_STRING = (
        "host=127.0.0.1 dbname=boxmayorista user=boxuser password=1234"
    )    

    # 🚀 AJUSTE PARA MAC - MLflow na porta 5001
    MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5001')
    
    # 🚀 AJUSTE PARA MAC - Flask na porta 5002
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5002'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    AIRFLOW_ENABLED = os.getenv('AIRFLOW_ENABLED', 'False') == 'True'