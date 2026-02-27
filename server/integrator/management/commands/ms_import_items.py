import pyodbc
import pandas as pd
from django.core.management.base import BaseCommand
from suppliers.models import Supplier
from items.models import Item

class Command(BaseCommand):
    help = 'Importa itens diretamente do SQL Server (bi_productos)'

    def handle(self, *args, **kwargs):
        try:
            # Conexão com SQL Server
            conn = pyodbc.connect(
                'DRIVER={FreeTDS};'
                'SERVER=192.168.30.8;'
                'PORT=1402;'
                'DATABASE=pegasus;'
                'UID=consulta;'
                'PWD=123consulta;'
                'TDS_Version=7.3;'
                'TrustServerCertificate=yes;'
            )

            query = """
                SELECT codigo, descripcion_producto, cant_paq, cant_min, unidad, precio_compra, precio_costo, tipo_fiscal, imp_imp, servicio, 
                nivel1, nivel2, nivel3, nivel4, nivel5, marca, precio_vta, codigo_barra, Desactivado_compra, desactivar_web, DESACTIVADO, POS, 
                desactivo_pgs, critico, PERECEDERO, COMPUESTO, Produccion, Seguro, descuento_NC, Percha, fleje, etiqueta, pesable, serie, 
                interes, bar_patio, mcc, restring, comanda, bonificacion_mobile, cod_proveedor_principal, proveedor_principal, precio_matriz
                FROM pegasus.dbo.bi_productos
            """

            df = pd.read_sql(query, conn)
            conn.close()

            count = 0
            for index, row in df.iterrows():
                try:
                    code = str(row['codigo']).strip()

                    # Ignora códigos inválidos
                    if not code or not code[0].isdigit():
                        self.stderr.write(self.style.WARNING(f'Linha {index + 2} ignorada: código inválido "{code}"'))
                        continue

                    item_data = {
                        'name': row['descripcion_producto'],
                        'pack_size': float(row['cant_paq']) if pd.notnull(row['cant_paq']) else None,
                        'min_size': int(row['cant_min']) if pd.notnull(row['cant_min']) else None,
                        'unit_of_measure': row['unidad'],
                        'purchase_price': float(row['precio_compra']) if pd.notnull(row['precio_compra']) else None,
                        'cost_price': float(row['precio_costo']) if pd.notnull(row['precio_costo']) else None,
                        'section': row['nivel1'],
                        'subsection': row['nivel2'],
                        'nivel3': row['nivel3'],
                        'nivel4': row['nivel4'],
                        'nivel5': row['nivel5'],
                        'brand': row['marca'],
                        'sale_price': float(row['precio_vta']) if pd.notnull(row['precio_vta']) else None,
                        'ean': str(row['codigo_barra']).strip() if pd.notnull(row['codigo_barra']) else None,
                        'is_disabled_purchase': bool(int(row['Desactivado_compra'])) if pd.notnull(row['Desactivado_compra']) else False,
                        'is_disabled': bool(int(row['DESACTIVADO'])) if pd.notnull(row['DESACTIVADO']) else False,
                        'matriz_price': float(row['precio_matriz']) if pd.notnull(row['precio_matriz']) else None,
                    }

                    supplier_code = str(row['cod_proveedor_principal']).strip()
                    supplier_name = row['proveedor_principal']

                    supplier, _ = Supplier.objects.update_or_create(
                        code=supplier_code,
                        defaults={'name': supplier_name, 'active': True}
                    )

                    item_data['supplier'] = supplier

                    Item.objects.update_or_create(
                        code=code,
                        defaults=item_data
                    )

                    count += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Erro na linha {index + 2}: {e}'))

            self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} itens importados/atualizados.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao conectar ou importar: {e}'))
