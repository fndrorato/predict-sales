import csv
import io
import psycopg2
import pyodbc
import time
from datetime import datetime
from flask import current_app
from threading import Thread
from psycopg2.extras import execute_values


# Variável global para progresso (pode melhorar com armazenagem compartilhada)
progress_state = {
    "percent": 0,
    "error": None
}

task_running = {
    'bi_productos': False,
    'orders': False,
    'stock': False
}

def truncate_numeric(value, precision=13, scale=2):
    if value is None:
        return None
    max_value = 10**(precision - scale) - 10**(-scale)
    if abs(value) > max_value:
        print(f"Valor {value} excede limite NUMERIC({precision},{scale}), truncando para {max_value}")
        value = max_value if value > 0 else -max_value
    # Truncar para scale decimal
    return round(value, scale)

def chunks(iterable, size):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

def transfer_bi_sucursales(sql_conn_str, pg_conn_str):
    try:
        query = 'SELECT cod_sucursal, nombre_sucursal FROM bi_sucursales'
        pg_table = 'stores_store'

        sql_conn = pyodbc.connect(sql_conn_str)
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute(query)
        data = sql_cursor.fetchall()
        sql_cursor.close()
        sql_conn.close()

        pg_conn = psycopg2.connect(pg_conn_str)
        pg_cursor = pg_conn.cursor()

        for row in data:
            code, name = row
            pg_cursor.execute(f"""
                INSERT INTO {pg_table} (code, name, active, created_at)
                VALUES (%s, %s, TRUE, NOW())
                ON CONFLICT (code) DO UPDATE
                SET name = EXCLUDED.name, active = TRUE;
            """, (code, name))

        pg_conn.commit()
        pg_cursor.close()
        pg_conn.close()

        return f"Tarefa 'Transferir Sucursais' concluída com sucesso!"

    except Exception as e:
        return f"Ocorreu erro: {str(e)}"

def transfer_bi_proveedores(sql_conn_str, pg_conn_str):
    global progress_state, task_running
    try:
        
        progress_state['percent'] = 0
        progress_state['error'] = None
        
        query = 'SELECT cod_proveedor, nombre_proveedor, ACTIVO FROM bi_proveedores'
        pg_table = 'suppliers_supplier'

        sql_conn = pyodbc.connect(sql_conn_str)
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute(query)
        data = sql_cursor.fetchall()
        
        total = len(data)
        print(f"Total de registros lidos do SQL Server: {total}")
                
        sql_cursor.close()
        sql_conn.close()

        pg_conn = psycopg2.connect(pg_conn_str)
        pg_cursor = pg_conn.cursor()
        
        processed = 0

        for row in data:
            code, name, active = row
            # Converter tipos e limpar strings se necessário
            code = int(code)
            name = name.strip()
            active = bool(active)

            pg_cursor.execute(f"""
                INSERT INTO {pg_table} (code, name, active, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                ON CONFLICT (code) DO UPDATE
                SET name = EXCLUDED.name,
                    active = EXCLUDED.active;
            """, (code, name, active))
            
            processed += 1

            progress_state['percent'] = int(processed / total * 100)
            print(f"Progresso: {progress_state['percent']}% ({processed}/{total})")            


        pg_conn.commit()
        pg_cursor.close()
        pg_conn.close()

        progress_state['percent'] = 100
        print("Transferência concluída com sucesso!")
        task_running['supplier'] = False

        return f"Tarefa 'Transferir Fornecedores' concluída com sucesso!"
    except Exception as e:
        progress_state['percent'] = 0
        task_running['supplier'] = False        
        return f"Ocorreu erro na transferência de fornecedores: {str(e)}"

def transfer_bi_productos(sql_conn_str, pg_conn_str, chunk_size=5000):
    global progress_state, task_running
    try:
        progress_state['percent'] = 0
        progress_state['error'] = None

        print("Iniciando transferência de produtos...")

        # ================= SQL Server =================
        print("Conectando ao SQL Server...")
        mssql_conn = pyodbc.connect(sql_conn_str)
        mssql_cursor = mssql_conn.cursor()
        print("Conexão SQL Server estabelecida.")

        query = """
            SELECT  codigo, descripcion_producto, cant_paq, cant_min, unidad, precio_compra, 
                    precio_costo, nivel1, nivel2, nivel3, nivel4, nivel5, marca, precio_vta, 
                    codigo_barra, Desactivado_compra, DESACTIVADO, precio_matriz,
                    cod_proveedor_principal, proveedor_principal
            FROM bi_productos;
        """
        mssql_cursor.execute(query)
        row = mssql_cursor.fetchone()

        if row:
            columns = [column[0] for column in mssql_cursor.description]
            for col_name, value in zip(columns, row):
                print(f"{col_name}: {value}")
        else:
            print("Nenhum registro encontrado.") 
                   
        rows = mssql_cursor.fetchall()
        total = len(rows)
        print(f"Total de registros lidos do SQL Server: {total}")

        # ================= PostgreSQL =================
        print("Conectando ao PostgreSQL...")
        pg_conn = psycopg2.connect(pg_conn_str)
        pg_cursor = pg_conn.cursor()
        print("Conexão PostgreSQL estabelecida.")

        processed = 0

        # ================= Loop em chunks =================
        print(f"Iniciando processamento em chunks de {chunk_size} registros...")
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = rows[start:end]

            supplier_values = []
            item_values = []

            for row in chunk:
                (
                    code, name, pack_size, min_size, unit_of_measure,
                    purchase_price, cost_price,
                    nivel1, nivel2, nivel3, nivel4, nivel5,
                    brand, sale_price, ean,
                    is_disabled_purchase, is_disabled,
                    matriz_price, supplier_code, supplier_name
                ) = row

                # Ajuste valores numéricos para caber no schema do banco:
                pack_size = truncate_numeric(pack_size)
                purchase_price = truncate_numeric(purchase_price)
                cost_price = truncate_numeric(cost_price)
                sale_price = truncate_numeric(sale_price)
                matriz_price = truncate_numeric(matriz_price)

                # suppliers
                if supplier_code:
                    supplier_values.append((
                        supplier_code,
                        supplier_name,
                        True,
                        datetime.utcnow()
                    ))

                # items
                item_values.append((
                    code, name, pack_size, min_size, unit_of_measure,
                    purchase_price, cost_price,
                    nivel1, nivel2, nivel3, nivel4, nivel5,
                    brand, sale_price, ean,
                    is_disabled_purchase, is_disabled,
                    matriz_price, supplier_code, datetime.utcnow()
                ))

            # ================= SUPPLIERS =================
            print("Upsert de fornecedores...")
            if supplier_values:
                print(f'Pré-processamento concluído. Fornecedores antes da deduplicação: {len(supplier_values)}')

                # Deduplicar fornecedores por código para evitar duplicatas no COPY
                unique_suppliers = {}
                for code, name, active, created_at in supplier_values:
                    unique_suppliers[code] = (name, active, created_at)

                supplier_values = [(code, *values) for code, values in unique_suppliers.items()]
                print(f'Fornecedores após deduplicação: {len(supplier_values)}')

                # Converte explicitamente code para int na geração do CSV
                output = io.StringIO()
                writer = csv.writer(output, delimiter='|', quoting=csv.QUOTE_MINIMAL)
                for code, name, active, created_at in supplier_values:
                    writer.writerow([int(code), name, active, created_at.isoformat()])
                output.seek(0)

                print('Preparando para criar (ou limpar) a tabela tmp_suppliers...')
                with pg_conn.cursor() as cur:
                    # Cria a tabela temporária com código do tipo INTEGER
                    cur.execute("""
                        CREATE TEMP TABLE tmp_suppliers (
                            code INTEGER PRIMARY KEY,
                            name TEXT,
                            active BOOLEAN,
                            created_at TIMESTAMP
                        )  ON COMMIT DROP;
                    """)
                    print("Tabela (temp) criada.")

                    # Trunca a tabela para evitar resíduos
                    cur.execute("TRUNCATE tmp_suppliers;")
                    print("Tabela tmp_suppliers truncada.")

                    try:
                        # Carrega dados via COPY
                        cur.copy_expert(
                            "COPY tmp_suppliers (code, name, active, created_at) FROM STDIN WITH (FORMAT CSV, DELIMITER '|')",
                            output
                        )
                        print("COPY executado.")
                    except Exception as e:
                        print("Erro no COPY:", e)
                        raise

                    # Conta quantas linhas foram carregadas
                    cur.execute("SELECT COUNT(*) FROM tmp_suppliers;")
                    row_count = cur.fetchone()[0]
                    print("Linhas carregadas em tmp_suppliers:", row_count)
                    if row_count == 0:
                        print("WARNING: Nenhum fornecedor carregado no batch!")

                    try:
                        # Upsert real na tabela final
                        cur.execute("""
                            INSERT INTO suppliers_supplier (code, name, active, created_at, updated_at)
                            SELECT code, name, active, created_at, NOW()
                            FROM tmp_suppliers
                            ON CONFLICT (code) DO UPDATE SET
                                name = EXCLUDED.name,
                                active = EXCLUDED.active,
                                updated_at = NOW()
                        """)

                        print("Upsert executado.")
                    except Exception as e:
                        print("Erro no upsert:", e)
                        raise

                    pg_conn.commit()
                    print("Commit realizado.")

            # ================= ITEMS =================
            print("Upsert de itens...")
            if item_values:
                # Deduplica por código
                unique_items = {}
                for row in item_values:
                    code = row[0]  # índice do código em item_values
                    unique_items[code] = row  # mantem o último registro para código duplicado

                item_values = list(unique_items.values())
                print(f"Itens após deduplicação: {len(item_values)}")

                output = io.StringIO()
                writer = csv.writer(output, delimiter='|', quoting=csv.QUOTE_MINIMAL)
                for row in item_values:
                # for row in filtered:
                    writer.writerow([v if v is not None else '' for v in row])
                output.seek(0)

                try:
                    with pg_conn.cursor() as cur:
                        cur.execute("""
                            CREATE TEMP TABLE IF NOT EXISTS tmp_items (
                                code TEXT,
                                name TEXT,
                                pack_size NUMERIC,
                                min_size INT,
                                unit_of_measure TEXT,
                                purchase_price NUMERIC,
                                cost_price NUMERIC,
                                nivel1 TEXT,
                                nivel2 TEXT,
                                nivel3 TEXT,
                                nivel4 TEXT,
                                nivel5 TEXT,
                                brand TEXT,
                                sale_price NUMERIC,
                                ean TEXT,
                                is_disabled_purchase BOOLEAN,
                                is_disabled BOOLEAN,
                                matriz_price NUMERIC,
                                supplier_code TEXT,
                                created_at TIMESTAMP
                            ) ON COMMIT DROP;
                        """)
                        print("Tabela temporária tmp_items criada.")
                        # Imprime o CSV completo para debugar
                        cur.copy_expert(
                            "COPY tmp_items FROM STDIN WITH (FORMAT CSV, DELIMITER '|')",
                            output
                        )
                        print("COPY para tmp_items executado.")
                      
                        # Relatório de fornecedores faltantes
                        cur.execute("""
                            SELECT DISTINCT t.supplier_code
                            FROM tmp_items t
                            WHERE t.supplier_code IS NOT NULL
                            AND NOT EXISTS (
                                SELECT 1
                                FROM suppliers_supplier s
                                WHERE s.code = t.supplier_code::integer
                            );
                        """)
                        missing_supplier_codes = cur.fetchall()
                        if missing_supplier_codes:
                            print("supplier_code(s) em tmp_items sem correspondente em suppliers_supplier (id):")
                            for scode, in missing_supplier_codes:
                                print(f"- {scode}")
                        else:
                            print("Todos supplier_code em tmp_items têm correspondente válido em suppliers_supplier.id")
                       

                        cur.execute("""
                            SELECT 
                                COUNT(*) AS count_null_or_invalid_suppliers
                            FROM tmp_items t
                            LEFT JOIN suppliers_supplier s ON s.code = t.supplier_code::integer
                            WHERE t.supplier_code IS NULL 
                            OR t.supplier_code = '' 
                            OR s.code IS NULL;
                        """)
                        count_null_suppliers = cur.fetchone()[0]
                        print(f"Total de itens com supplier_code inválido ou nulo (resultando em supplier_id NULL): {count_null_suppliers}")

                        # Atualiza supplier_code '0' para nulos/vazios
                        cur.execute("""
                            UPDATE tmp_items SET supplier_code = '0'
                            WHERE supplier_code IS NULL OR supplier_code = '';
                        """)

                        cur.execute("""
                            INSERT INTO items_item (
                                code, name, pack_size, min_size, unit_of_measure,
                                purchase_price, cost_price, section, subsection, nivel3, nivel4, nivel5,
                                brand, sale_price, ean, is_disabled_purchase, is_disabled, matriz_price,
                                supplier_id, created_at, updated_at
                            )
                            SELECT
                                t.code, t.name, t.pack_size, t.min_size, t.unit_of_measure,
                                t.purchase_price, t.cost_price,
                                t.nivel1 AS section,    -- ajuste feito aqui
                                t.nivel2 AS subsection, -- e aqui
                                t.nivel3, t.nivel4, t.nivel5,
                                t.brand, t.sale_price, t.ean, t.is_disabled_purchase, t.is_disabled, t.matriz_price,
                                s.code, t.created_at, now()
                            FROM tmp_items t
                            LEFT JOIN suppliers_supplier s ON s.code = t.supplier_code::integer
                            ON CONFLICT (code) DO UPDATE SET
                                name = EXCLUDED.name,
                                pack_size = EXCLUDED.pack_size,
                                min_size = EXCLUDED.min_size,
                                unit_of_measure = EXCLUDED.unit_of_measure,
                                purchase_price = EXCLUDED.purchase_price,
                                cost_price = EXCLUDED.cost_price,
                                section = EXCLUDED.section,
                                subsection = EXCLUDED.subsection,
                                nivel3 = EXCLUDED.nivel3,
                                nivel4 = EXCLUDED.nivel4,
                                nivel5 = EXCLUDED.nivel5,
                                brand = EXCLUDED.brand,
                                sale_price = EXCLUDED.sale_price,
                                ean = EXCLUDED.ean,
                                is_disabled_purchase = EXCLUDED.is_disabled_purchase,
                                is_disabled = EXCLUDED.is_disabled,
                                matriz_price = EXCLUDED.matriz_price,
                                supplier_id = EXCLUDED.supplier_id;
                        """)
                        print("Upsert em items_item executado.")
                        pg_conn.commit()
                        print("Commit realizado.")

                except Exception as e:
                    print("Erro na transferência dos itens:", e)
                    progress_state['percent'] = 0
                    progress_state['error'] = str(e)
                    task_running['bi_productos'] = False
                    pg_conn.rollback()
                    return f"Erro na transferência de produtos: {str(e)}"

            # ================= Commit e progresso =================
            pg_conn.commit()
            processed += len(chunk)

            progress_state['percent'] = int(processed / total * 100)
            print(f"Progresso: {progress_state['percent']}% ({processed}/{total})")

        # ================= Finalização =================
        mssql_cursor.close()
        mssql_conn.close()
        pg_cursor.close()
        pg_conn.close()

        progress_state['percent'] = 100
        print("Transferência concluída com sucesso!")
        task_running['bi_productos'] = False
        return f"Transferência concluída! Total processado: {processed} registros."

    except Exception as e:
        progress_state['percent'] = 0
        task_running['bi_productos'] = False
        return f"Erro na transferência de produtos: {str(e)}"

def transfer_orders(sql_conn_str, pg_conn_str, chunk_size=5000):
    global progress_state, task_running
    progress_state['orders'] = {"percent": 0, "error": None}
    try:
        print("Conectando ao SQL Server...")
        mssql_conn = pyodbc.connect(sql_conn_str)
        mssql_cursor = mssql_conn.cursor()

        # Query SQL Server
        query = """
        SELECT ocfe.COD_SUCURSAL as sucursal, r.nro_pedido, ocfe.importe, ocfe.ABIERTA as abierta, 
            r.fecha, ocfe.FECHA_ENTREGA as fecha_prevista, ocfe.fec_recep as fecha_recepcion,
            r.cod_proveedor, r.codigo, r.cantidad_ped, r.cantidad_recep, ocfe.precio
        FROM pegasus.dbo.view_powerbi_recepcion_mercaderias as r,
        (
            SELECT DISTINCT NRO_OC, COD_SUCURSAL, FECHA_ENTREGA, ABIERTA, fec_recep, importe, codigo, precio
            FROM pegasus.dbo.view_powerbi_OC as oc
        ) as ocfe
        WHERE r.fecha >= '2025-07-01'
        AND r.nro_pedido = ocfe.NRO_OC
        AND r.codigo = ocfe.codigo
        ORDER BY r.nro_pedido DESC;
        """
        mssql_cursor.execute(query)
        rows = mssql_cursor.fetchall()
        total = len(rows)
        print(f"Total de ordens lidas: {total}")

        print("Conectando ao PostgreSQL...")
        pg_conn = psycopg2.connect(pg_conn_str)
        processed = 0

        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = rows[start:end]

            order_values = []
            for row in chunk:
                (
                    sucursal, nro_pedido, importe, abierta,
                    fecha, fecha_prevista, fecha_recepcion,
                    cod_proveedor, codigo,
                    cantidad_ped, cantidad_recep, precio
                ) = row

                order_values.append([
                    int(nro_pedido),
                    int(sucursal),
                    int(cod_proveedor),
                    str(codigo).strip(),
                    float(importe) if importe else 0.0,
                    bool(int(abierta)) if abierta is not None else False,
                    str(fecha).split(' ')[0] if fecha else None,
                    str(fecha_prevista).split(' ')[0] if fecha_prevista else None,
                    str(fecha_recepcion).split(' ')[0] if fecha_recepcion else None,
                    float(cantidad_ped) if cantidad_ped else 0.0,
                    float(cantidad_recep) if cantidad_recep else 0.0,
                    float(precio) if precio else 0.0
                ])

            with pg_conn.cursor() as cur:
                # Tabela temporária p/ ordens
                cur.execute("""
                    CREATE TEMP TABLE IF NOT EXISTS tmp_orders (
                        oc_number INTEGER,
                        store_code INTEGER,
                        supplier_code INTEGER,
                        item_code TEXT,
                        total_amount NUMERIC,
                        is_open BOOLEAN,
                        date DATE,
                        expected_date DATE,
                        received_date DATE,
                        quantity_order NUMERIC,
                        quantity_received NUMERIC,
                        price NUMERIC
                    ) ON COMMIT DROP;
                """)
                cur.execute("TRUNCATE tmp_orders;")

                # CSV para COPY
                output = io.StringIO()
                writer = csv.writer(output, delimiter='|', quoting=csv.QUOTE_MINIMAL)
                for vals in order_values:
                    writer.writerow([v if v is not None else '' for v in vals])
                output.seek(0)

                cur.copy_expert(
                    "COPY tmp_orders FROM STDIN WITH (FORMAT CSV, DELIMITER '|')",
                    output
                )

                # Upsert para orders_ordersystem
                cur.execute("""
                    INSERT INTO orders_ordersystem (
                        oc_number, item_id, store_id, supplier_id, total_amount,
                        is_open, date, expected_date, received_date,
                        quantity_order, quantity_received, price,
                        created_at, updated_at
                    )
                    SELECT
                        t.oc_number,
                        i.code AS item_id,
                        st.code AS store_id,
                        s.code AS supplier_id, 
                        MAX(t.total_amount) AS total_amount,
                        MAX(t.is_open::int)::boolean AS is_open, 
                        MAX(t.date) AS date,
                        MAX(t.expected_date) AS expected_date,
                        MAX(t.received_date) AS received_date,
                        MAX(t.quantity_order) AS quantity_order,
                        MAX(t.quantity_received) AS quantity_received,
                        MAX(t.price) AS price,
                        NOW() AS created_at,
                        NOW() AS updated_at
                    FROM tmp_orders t
                    LEFT JOIN items_item i ON i.code = t.item_code
                    LEFT JOIN stores_store st ON st.code = t.store_code
                    LEFT JOIN suppliers_supplier s ON s.code = t.supplier_code
                    GROUP BY
                        t.oc_number,
                        i.code,
                        st.code,
                        s.code 
                    ON CONFLICT (oc_number, item_id, store_id) DO UPDATE SET
                        total_amount = EXCLUDED.total_amount,
                        is_open = EXCLUDED.is_open,
                        date = EXCLUDED.date,
                        expected_date = EXCLUDED.expected_date,
                        received_date = EXCLUDED.received_date,
                        quantity_order = EXCLUDED.quantity_order,
                        quantity_received = EXCLUDED.quantity_received,
                        price = EXCLUDED.price,
                        updated_at = now();
                """)
                pg_conn.commit()                

            processed += len(chunk)
            progress_state['orders']['percent'] = int(processed / total * 100)
            print(f"Progresso: {progress_state['orders']['percent']}% ({processed}/{total})")

        mssql_cursor.close()
        mssql_conn.close()
        pg_conn.close()

        progress_state['orders']['percent'] = 100
        task_running['orders'] = False
        print("Transferência de ordens concluída!")
        return "Transferência de ordens concluída!"

    except Exception as e:
        progress_state['orders']['percent'] = 0
        progress_state['orders']['error'] = str(e)
        task_running['orders'] = False
        print("Erro ao transferir ordens:", e)
        return f"Erro: {str(e)}"

def transfer_stock(sql_conn_str, pg_conn_str, chunk_size=5000):
    global progress_state, task_running
    progress_state['stock'] = {"percent": 0, "error": None}
    try:
        print("Conectando ao SQL Server...")
        mssql_conn = pyodbc.connect(sql_conn_str)
        mssql_cursor = mssql_conn.cursor()

        query = """
            SELECT bs.codigo, bs.cod_sucursal, MAX(bs.cantidad) AS cantidad
            FROM bi_stock bs
            GROUP BY bs.codigo, bs.cod_sucursal
        """
        mssql_cursor.execute(query)
        rows = mssql_cursor.fetchall()
        total = len(rows)
        print(f"Total de itens de estoque lidos: {total}")

        print("Conectando ao PostgreSQL...")
        pg_conn = psycopg2.connect(pg_conn_str)
        processed = 0

        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = rows[start:end]

            stock_values = []
            for row in chunk:
                codigo, cod_sucursal, cantidad = row
                stock_values.append([
                    str(codigo).strip(),
                    str(cod_sucursal).strip(),
                    float(cantidad) if cantidad is not None else 0.0
                ])

            with pg_conn.cursor() as cur:
                cur.execute("""
                    CREATE TEMP TABLE IF NOT EXISTS tmp_stock (
                        item_code TEXT,
                        store_code TEXT,
                        stock_available NUMERIC
                    ) ON COMMIT DROP;
                """)
                cur.execute("TRUNCATE tmp_stock;")

                output = io.StringIO()
                writer = csv.writer(output, delimiter='|', quoting=csv.QUOTE_MINIMAL)
                for vals in stock_values:
                    writer.writerow([v if v is not None else '' for v in vals])
                output.seek(0)

                cur.copy_expert(
                    "COPY tmp_stock FROM STDIN WITH (FORMAT CSV, DELIMITER '|')",
                    output
                )

                # Atualização/Upsert do estoque
                # Se não existe, cria. Se existe, atualiza.
                # Ajuste: usa ON CONFLICT com constraint única em (item_id, store_id)
                cur.execute("""
                    INSERT INTO items_itemcontrolstock (
                        item_id, store_id, stock_available, stock_available_on,
                        date_last_purchase, quantity_last_purchase,
                        days_stock, 
                        stock_min,
                        sales_frequency
                    )
                    SELECT
                        t.item_code,
                        t.store_code::integer,
                        t.stock_available,
                        CURRENT_DATE,
                        os.max_date_last_purchase,
                        COALESCE(os.max_quantity_last_purchase, 0.00),
                        0,
                        0.00,
                        0.00
                    FROM tmp_stock t
                    LEFT JOIN (
                        SELECT
                            o.item_id,
                            o.store_id,
                            MAX(o.received_date) AS max_date_last_purchase,
                            COALESCE(MAX(o.quantity_received), 0.00) AS max_quantity_last_purchase 
                        FROM orders_ordersystem o
                        WHERE o.quantity_received > 0
                        GROUP BY o.item_id, o.store_id
                    ) os
                    ON os.item_id = t.item_code AND os.store_id = t.store_code::integer
                    ON CONFLICT (item_id, store_id) DO UPDATE SET
                        stock_available = EXCLUDED.stock_available,
                        stock_available_on = CURRENT_DATE,
                        date_last_purchase = EXCLUDED.date_last_purchase,
                        quantity_last_purchase = EXCLUDED.quantity_last_purchase;
                """)
                pg_conn.commit()

            processed += len(chunk)
            progress_state['stock']['percent'] = int(processed / total * 100)
            print(f"Progresso: {progress_state['stock']['percent']}% ({processed}/{total})")

        mssql_cursor.close()
        mssql_conn.close()
        pg_conn.close()

        progress_state['stock']['percent'] = 100
        task_running['stock'] = False
        print("Transferência de estoque concluída!")
        return "Transferência de estoque concluída!"

    except Exception as e:
        progress_state['stock']['percent'] = 0
        progress_state['stock']['error'] = str(e)
        task_running['stock'] = False
        print("Erro ao transferir estoque:", e)
        return f"Erro: {str(e)}"

def transfer_sales(sql_conn_str, pg_conn_str, chunk_size=5000):

    global progress_state, task_running
    progress_state['sales'] = {"percent": 0, "error": None}
    
    try:
        # Conexão PostgreSQL
        pg_conn = psycopg2.connect(pg_conn_str)
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("SELECT COALESCE(MAX(date), '2000-01-01') FROM sales_sale;")
        max_date = pg_cursor.fetchone()[0]
        print(f"Maior data já gravada em Sale: {max_date}")

        today_str = datetime.today().strftime('%Y-%m-%d')

        # Conexão SQL Server
        mssql_conn = pyodbc.connect(sql_conn_str)
        mssql_cursor = mssql_conn.cursor()
        sql_server_query = f"""
            SELECT bcv.nro_reg, bcv.fecha, bcv.hora, bcv.nro_factura, 
                   bcv.cod_sucursal, bcv.codigo, bcv.cant_vta, bcv.ventas_det_precio_neto 
            FROM pegasus.dbo.bi_compra_venta AS bcv
            WHERE bcv.tipo = 'VENTA'
              AND bcv.fecha > '{max_date}'
              AND bcv.fecha < '{today_str}'
            ORDER BY bcv.nro_reg DESC
        """
        mssql_cursor.execute(sql_server_query)
        rows = mssql_cursor.fetchall()
        total = len(rows)
        print(f"Registros de venda filtrados para importação: {total}")

        # Cache de lojas e itens como sets para verificação de existência
        pg_cursor.execute("SELECT code FROM stores_store;")
        store_codes = {str(code).strip() for (code,) in pg_cursor.fetchall()}

        pg_cursor.execute("SELECT code FROM items_item;")
        item_codes = {str(code).strip() for (code,) in pg_cursor.fetchall()}

        # Processamento em chunks
        processed = 0

        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = rows[start:end]
            sale_values = []

            for row in chunk:
                try:
                    nro_reg, fecha, hora, nro_factura, cod_sucursal, codigo, cant_vta, ventas_det_precio_neto = row
                    ticket_number = str(nro_factura).strip().strip('"')
                    date = fecha.date() if hasattr(fecha, 'date') else fecha  # já datetime
                    time = int(hora)
                    store_code = str(cod_sucursal).strip()
                    item_code = str(codigo).strip()

                    # Verifique existência no cadastro de lojas e itens
                    if store_code not in store_codes or item_code not in item_codes:
                        continue

                    # Converta os códigos para inteiro para garantir compatibilidade com bigint/integer
                    store_id_int = int(store_code)
                    item_id_int = int(item_code)

                    quantity = float(str(cant_vta).replace(',', '.'))
                    price = float(str(ventas_det_precio_neto).replace(',', '.'))

                    sale_values.append((
                        ticket_number,
                        store_id_int,
                        date,
                        time,
                        item_id_int,
                        quantity,
                        price,
                        datetime.now()  # created_at
                    ))

                except Exception as e:
                    print(f"Erro ao processar linha: {row}\n{e}")

            with pg_conn.cursor() as cur:
                output = io.StringIO()
                writer = csv.writer(output, delimiter='|', quoting=csv.QUOTE_MINIMAL)
                for vals in sale_values:
                    writer.writerow([v if v is not None else '' for v in vals])
                output.seek(0)

                cur.execute("""
                    CREATE TEMP TABLE IF NOT EXISTS tmp_sales (
                        ticket_number TEXT,
                        store_id INTEGER,
                        date DATE,
                        time INTEGER,
                        item_id BIGINT,
                        quantity NUMERIC,
                        price NUMERIC,
                        created_at TIMESTAMP
                    ) ON COMMIT DROP;
                """)
                cur.execute("TRUNCATE tmp_sales;")
                cur.copy_expert(
                    "COPY tmp_sales FROM STDIN WITH (FORMAT CSV, DELIMITER '|')",
                    output
                )

                # Inserção em sales_sale
                cur.execute("""
                    INSERT INTO sales_sale (
                        ticket_number, store_id, date, time, item_id, quantity, price, created_at
                    )
                    SELECT
                        ticket_number, store_id, date, time, item_id, quantity, price, created_at
                    FROM tmp_sales;
                """)
                pg_conn.commit()

            processed += len(chunk)
            progress_state['sales']['percent'] = int(processed / total * 100)
            print(f"Progresso: {progress_state['sales']['percent']}% ({processed}/{total})")

        mssql_cursor.close()
        mssql_conn.close()
        pg_cursor.close()
        pg_conn.close()

        progress_state['sales']['percent'] = 100
        task_running['sales'] = False
        print("Transferência de vendas concluída!")
        return "Transferência de vendas concluída!"

    except Exception as e:
        progress_state['sales']['percent'] = 0
        progress_state['sales']['error'] = str(e)
        task_running['sales'] = False
        print("Erro ao transferir vendas:", e)
        return f"Erro: {str(e)}"


def transfer_bi_productos_async(sql_conn_str, pg_conn_str):
    """
    Wrapper que chama a função pesada acima dentro da thread.
    """
    try:
        print("Iniciando transferência de produtos em background...")
        transfer_bi_productos(sql_conn_str, pg_conn_str)
    except Exception:
        # Em caso de erro, pode-se expor um outro estado/endpoint de erro
        progress_state['percent'] = 0

def start_transfer_productos_thread(sql_conn_str, pg_conn_str):
    t = Thread(target=transfer_bi_productos_async, args=(sql_conn_str, pg_conn_str), daemon=True)
    t.start()

def transfer_orders_async(sql_conn_str, pg_conn_str):
    try:
        print("Iniciando transferência de ordens em background...")
        transfer_orders(sql_conn_str, pg_conn_str)
    except Exception:
        progress_state['orders']['percent'] = 0
        progress_state['orders']['error'] = "Erro na thread de ordens"
        task_running['orders'] = False

def start_transfer_orders_thread(sql_conn_str, pg_conn_str):
    t = Thread(target=transfer_orders_async, args=(sql_conn_str, pg_conn_str), daemon=True)
    t.start()

def transfer_stock_async(sql_conn_str, pg_conn_str):
    try:
        transfer_stock(sql_conn_str, pg_conn_str)
    except Exception:
        progress_state['stock']['percent'] = 0
        progress_state['stock']['error'] = "Erro na thread de estoque"
        task_running['stock'] = False

def start_transfer_stock_thread(sql_conn_str, pg_conn_str):
    t = Thread(target=transfer_stock_async, args=(sql_conn_str, pg_conn_str), daemon=True)
    t.start()

def transfer_sales_async(sql_conn_str, pg_conn_str):
    try:
        transfer_sales(sql_conn_str, pg_conn_str)
    except Exception:
        progress_state['sales']['percent'] = 0
        progress_state['sales']['error'] = "Erro na thread de vendas"
        task_running['sales'] = False

def start_transfer_sales_thread(sql_conn_str, pg_conn_str):
    t = Thread(target=transfer_sales_async, args=(sql_conn_str, pg_conn_str), daemon=True)
    t.start()
