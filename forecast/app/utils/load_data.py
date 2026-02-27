# app/utils/load_data.py

import psycopg2
import pandas as pd
from datetime import datetime


def get_available_stores(pg_conn_str):
    """
    Busca lojas disponíveis no banco de dados
    
    Args:
        pg_conn_str: String de conexão PostgreSQL
    
    Returns:
        list: Lista de dicts com store_id e store_name
        
    Raises:
        Exception: Se houver erro na conexão ou query
    """
    print("🔍 Buscando lojas disponíveis...")
    try:
        # Conectar ao banco
        conn = psycopg2.connect(pg_conn_str)
        
        # Query para buscar lojas ativas
        query = """
            SELECT DISTINCT s.store_id, st.name as store_name
            FROM public.sales_sale s
            LEFT JOIN public.stores_store st ON s.store_id = st.code
            WHERE s.date >= CURRENT_DATE - INTERVAL '180 days'
            ORDER BY s.store_id
        """
        
        # Executar query
        stores_df = pd.read_sql(query, conn)
        conn.close()
        
        # Converter para lista de dicts
        stores = stores_df.to_dict('records')
        
        # Se não tem nome, usar ID como fallback
        for store in stores:
            if not store['store_name'] or pd.isna(store['store_name']):
                store['store_name'] = f"Loja {store['store_id']}"
        
        return stores
        
    except psycopg2.Error as e:
        print(f"❌ Erro de banco de dados: {e}")
        raise Exception(f"Erro ao buscar lojas: {str(e)}")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        raise Exception(f"Erro ao processar lojas: {str(e)}")


def get_stores_with_item_count(pg_conn_str):
    """
    Busca lojas com contagem de itens ativos
    
    Args:
        pg_conn_str: String de conexão PostgreSQL
    
    Returns:
        list: Lista de dicts com store_id, store_name e item_count
    """
    print("🔍 Buscando lojas com contagem de itens...")
    try:
        conn = psycopg2.connect(pg_conn_str)
        
        query = """
            SELECT 
                s.store_id, 
                st.name as store_name,
                COUNT(DISTINCT s.item_id) as item_count,
                COUNT(*) as total_sales
            FROM public.sales_sale s
            LEFT JOIN public.stores_store st ON s.store_id = st.code
            JOIN public.items_item i ON s.item_id = i.code::int
            WHERE s.date >= CURRENT_DATE - INTERVAL '180 days'
              AND i.is_disabled_purchase = false
            GROUP BY s.store_id, st.name
            HAVING COUNT(DISTINCT s.item_id) >= 10
            ORDER BY s.store_id
        """
        
        stores_df = pd.read_sql(query, conn)
        conn.close()
        
        stores = stores_df.to_dict('records')
        
        # Formatar nomes
        for store in stores:
            if not store['store_name'] or pd.isna(store['store_name']):
                store['store_name'] = f"Loja {store['store_id']}"
            
            # Formatar números
            store['item_count'] = int(store['item_count'])
            store['total_sales'] = int(store['total_sales'])
        
        return stores
        
    except Exception as e:
        print(f"❌ Erro ao buscar lojas com contagem: {e}")
        raise Exception(f"Erro: {str(e)}")


def validate_store_ids(pg_conn_str, store_ids):
    """
    Valida se os store_ids existem no banco
    
    Args:
        pg_conn_str: String de conexão
        store_ids: Lista de IDs para validar
    
    Returns:
        dict: {
            'valid': [ids válidos],
            'invalid': [ids inválidos]
        }
    """
    print("🔍 Validando store_ids...")
    try:
        conn = psycopg2.connect(pg_conn_str)
        
        # Buscar lojas existentes
        stores_str = ', '.join(map(str, store_ids))
        query = f"""
            SELECT DISTINCT store_id
            FROM public.sales_sale
            WHERE store_id IN ({stores_str})
        """
        
        existing_df = pd.read_sql(query, conn)
        conn.close()
        
        existing_ids = existing_df['store_id'].tolist()
        invalid_ids = [sid for sid in store_ids if sid not in existing_ids]
        
        return {
            'valid': existing_ids,
            'invalid': invalid_ids
        }
        
    except Exception as e:
        print(f"❌ Erro ao validar store_ids: {e}")
        raise Exception(f"Erro na validação: {str(e)}")