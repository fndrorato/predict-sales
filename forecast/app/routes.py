# app/routes.py
from flask import current_app as app, render_template, request, jsonify
from .transfer import transfer_bi_sucursales, transfer_bi_proveedores, transfer_bi_productos
from .transfer import progress_state, start_transfer_productos_thread
from .transfer import start_transfer_orders_thread, start_transfer_stock_thread
from .transfer import start_transfer_sales_thread
from .forecasting_service import (
    main_forecast_pipeline, 
    save_forecasts_to_db,
    FORECAST_STATUS,
    FORECAST_TASK_RUNNING
)
from app.utils.load_data import get_available_stores, get_stores_with_item_count, validate_store_ids
import threading
from threading import Thread
import time
from .config import Config

transfer_tasks = {
    'bi_sucursales': {
        'button_label': 'Transferir Sucursais',
    },
    'bi_proveedores': {
        'button_label': 'Transferir Fornecedores',
    },  
}

task_running = {'bi_productos': False}

@app.route('/', methods=['GET', 'POST'])
def home():
    message = None

    if request.method == 'POST':
        task = request.form.get('task')

        if task == 'bi_sucursales':
            message = transfer_bi_sucursales(Config.SQLSERVER_CONNECTION_STRING, Config.POSTGRES_CONNECTION_STRING)

        elif task == 'bi_proveedores':
            message = transfer_bi_proveedores(Config.SQLSERVER_CONNECTION_STRING, Config.POSTGRES_CONNECTION_STRING)

        elif task == 'bi_productos':
            if task_running.get('bi_productos'):
                message = "Transferência de Produtos já está em andamento."
            else:
                message = "Transferência de Produtos iniciada em background."

    # ✅ CORRIGIDO - SEM "../templates/"
    return render_template('transfer.html', transfer_tasks=transfer_tasks, message=message)

@app.route('/start_transfer', methods=['POST'])
def start_transfer():
    print("Recebida requisição para iniciar transferência de produtos.")

    if not task_running.get('bi_productos'):
        print("Iniciando thread de transferência de produtos.")
        task_running['bi_productos'] = True
        progress_state['percent'] = 0
        start_transfer_productos_thread(Config.SQLSERVER_CONNECTION_STRING, Config.POSTGRES_CONNECTION_STRING)
        return jsonify({"status": "started", "message": "Transferência iniciada em background"})
    else:
        return jsonify({"status": "already_running", "message": "Já existe uma transferência em andamento"})

@app.route('/progress', methods=['GET'])
def progress():
    return jsonify({
        "progress": progress_state.get("percent", 0),
        "error": progress_state.get("error")
    })

@app.route('/progress_orders', methods=['GET'])
def progress_orders():
    state = progress_state.get("orders", {"percent": 0, "error": None})
    return jsonify({"progress": state.get("percent", 0), "error": state.get("error")})

@app.route('/start_transfer_orders', methods=['POST'])
def start_transfer_orders():
    print("Recebida requisição para transferir ordens de compra.")
    if not task_running.get('orders'):
        print("Iniciando thread de transferência de ordens.")
        task_running['orders'] = True
        progress_state['orders'] = {"percent": 0, "error": None}
        start_transfer_orders_thread(Config.SQLSERVER_CONNECTION_STRING, Config.POSTGRES_CONNECTION_STRING)
        return jsonify({"status": "started", "message": "Transferência de ordens iniciada em background"})
    else:
        return jsonify({"status": "already_running", "message": "Já existe uma transferência de ordens em andamento"})
  
@app.route('/start_transfer_suppliers', methods=['POST'])
def start_transfer_suppliers():
    if not task_running.get('supplier'):
        print("Iniciando thread de transferência de fornecedores.")
        task_running['supplier'] = True
        progress_state['supplier'] = {"percent": 0, "error": None}
        transfer_bi_proveedores(Config.SQLSERVER_CONNECTION_STRING, Config.POSTGRES_CONNECTION_STRING)
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already_running"})

@app.route('/progress_suppliers', methods=['GET'])
def progress_suppliers():
    state = progress_state.get("supplier", {"percent": 0, "error": None})
    return jsonify({"progress": state.get("percent", 0), "error": state.get("error")})    

@app.route('/start_transfer_stock', methods=['POST'])
def start_transfer_stock():
    if not task_running.get('stock'):
        print("Iniciando thread de transferência de estoque.")
        task_running['stock'] = True
        progress_state['stock'] = {"percent": 0, "error": None}
        start_transfer_stock_thread(Config.SQLSERVER_CONNECTION_STRING, Config.POSTGRES_CONNECTION_STRING)
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already_running"})

@app.route('/progress_stock', methods=['GET'])
def progress_stock():
    state = progress_state.get("stock", {"percent": 0, "error": None})
    return jsonify({"progress": state.get("percent", 0), "error": state.get("error")})

@app.route('/start_transfer_sales', methods=['POST'])
def start_transfer_sales():
    if not task_running.get('sales'):
        print("Iniciando thread de transferência de vendas.")
        task_running['sales'] = True
        progress_state['sales'] = {"percent": 0, "error": None}
        start_transfer_sales_thread(Config.SQLSERVER_CONNECTION_STRING, Config.POSTGRES_CONNECTION_STRING)
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already_running"})

@app.route('/progress_sales', methods=['GET'])
def progress_sales():
    state = progress_state.get("sales", {"percent": 0, "error": None})
    return jsonify({"progress": state.get("percent", 0), "error": state.get("error")})

def run_forecast_task_in_background():
    """Função wrapper para rodar o pipeline na thread e atualizar o status."""
    global FORECAST_TASK_RUNNING
    
    FORECAST_STATUS.update({'progress': 0, 'total': 0, 'completed': 0, 'error': None, 'data': None})
    FORECAST_TASK_RUNNING = True

    try:
        results, summary = main_forecast_pipeline(Config.POSTGRES_CONNECTION_STRING)
        
        if summary is not None and not summary.empty:
            FORECAST_STATUS['progress'] = 95 
            
            save_forecasts_to_db(summary, Config.POSTGRES_CONNECTION_STRING)
            
            FORECAST_STATUS['data'] = summary.to_dict('records')
            FORECAST_STATUS['progress'] = 100
            message = f"Previsão concluída com sucesso! {len(summary)} registros salvos."
        else:
            message = "Previsão concluída, mas nenhum dado gerado."

        FORECAST_STATUS['total'] = len(summary) if summary is not None else 0
        
    except Exception as e:
        FORECAST_STATUS['error'] = str(e)
        FORECAST_STATUS['progress'] = -1
        message = f"Erro fatal durante a previsão: {e}"
        
    finally:
        FORECAST_TASK_RUNNING = False
        print(message)

@app.route("/forecast", methods=["GET"])
def forecast_page():
    """Renderiza a página principal de forecast (GET)"""
    # ✅ CORRIGIDO - SEM "../templates/"
    return render_template("forecast.html", message=None, status=FORECAST_STATUS)

# ==========================================
# ROTA START FORECAST (COM VALIDAÇÃO)
# ==========================================

@app.route('/start_forecast', methods=['POST'])
def start_forecast():
    """Inicia o forecast para as lojas selecionadas"""
    global FORECAST_TASK_RUNNING
    
    if FORECAST_TASK_RUNNING:
        return jsonify({
            'status': 'running',
            'message': 'Forecast já está em execução'
        })
    
    # Pegar store_ids do request
    data = request.get_json()
    store_ids = data.get('store_ids', [])
    
    if not store_ids:
        return jsonify({
            'status': 'error',
            'message': 'Nenhuma loja selecionada'
        }), 400
    
    # ✅ VALIDAR STORE_IDS ANTES DE PROCESSAR
    try:
        validation = validate_store_ids(Config.POSTGRES_CONNECTION_STRING, store_ids)
        
        if validation['invalid']:
            return jsonify({
                'status': 'error',
                'message': f"Lojas inválidas: {validation['invalid']}",
                'invalid_stores': validation['invalid']
            }), 400
        
        # Usar apenas IDs válidos
        store_ids = validation['valid']
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Erro ao validar lojas: {str(e)}"
        }), 500
    
    print(f"🏪 Lojas selecionadas (validadas): {store_ids}")
    
    # Resetar status
    FORECAST_STATUS['progress'] = 0
    FORECAST_STATUS['error'] = None
    FORECAST_STATUS['data'] = None
    
    # Thread para executar forecast
    def run_pipeline():
        global FORECAST_TASK_RUNNING
        try:
            FORECAST_TASK_RUNNING = True
            
            from app.forecasting_service import main_forecast_pipeline
            
            result_df, summary_df = main_forecast_pipeline(
                Config.POSTGRES_CONNECTION_STRING,
                forecast_periods=60,
                source='web_ui',
                executed_by='user',
                store_ids=store_ids
            )
            
            FORECAST_STATUS['data'] = {
                'total': len(result_df),
                'stores': store_ids,
                'summary': summary_df.to_dict() if not summary_df.empty else {}
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            FORECAST_STATUS['error'] = str(e)
        finally:
            FORECAST_TASK_RUNNING = False
    
    thread = threading.Thread(target=run_pipeline)
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': f'Forecast iniciado para {len(store_ids)} loja(s)',
        'stores': store_ids
    })

@app.route("/forecast_progress", methods=["GET"])
def forecast_progress():
    """Rota para o JavaScript fazer o polling e verificar o status e %."""
    
    if not FORECAST_TASK_RUNNING and FORECAST_STATUS['data'] is not None:
        return jsonify({
            'progress': 100,
            'status': 'completed',
            'data': FORECAST_STATUS['data'] 
        })
    
    if FORECAST_STATUS['error']:
         return jsonify({'progress': -1, 'status': 'error', 'error': FORECAST_STATUS['error']})

    return jsonify({
        'progress': FORECAST_STATUS['progress'],
        'status': 'running'
    })
    
# ==========================================
# ROTA PARA BUSCAR LOJAS (SIMPLES)
# ==========================================

@app.route('/get_stores', methods=['GET'])
def get_stores():
    """Retorna lista de lojas disponíveis"""
    try:
        # ✅ CHAMAR A FUNÇÃO DO utils/load_data.py
        stores = get_available_stores(Config.POSTGRES_CONNECTION_STRING)
        
        return jsonify({
            'status': 'success',
            'stores': stores,
            'total': len(stores)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==========================================
# ROTA PARA BUSCAR LOJAS (COM DETALHES)
# ==========================================

@app.route('/get_stores_detailed', methods=['GET'])
def get_stores_detailed():
    """Retorna lojas com contagem de itens"""
    try:
        # ✅ CHAMAR A FUNÇÃO COM MAIS DETALHES
        stores = get_stores_with_item_count(Config.POSTGRES_CONNECTION_STRING)
        
        return jsonify({
            'status': 'success',
            'stores': stores,
            'total': len(stores)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
