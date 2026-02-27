import os
import csv
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from stores.models import Store

load_dotenv()

class Command(BaseCommand):
    help = 'Importa lojas de um arquivo CSV localizado na mesma pasta do comando'

    def handle(self, *args, **kwargs):
        # Define o caminho para o arquivo CSV (mesmo diretório do script)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'data/bi_sucursales.csv')

        try:
            # Abre o arquivo CSV
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader)  # Pula o cabeçalho ("cod_sucursal";"nombre_sucursal")

                count = 0
                for row in reader:
                    code, name = row
                    # Converte o código para inteiro (caso seja necessário)
                    code = int(code.strip())
                    name = name.strip()

                    # Cria ou atualiza a loja no banco de dados
                    store, created = Store.objects.update_or_create(
                        code=code,
                        defaults={'name': name, 'active': True}
                    )
                    count += 1

                self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} lojas importadas/atualizadas.'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Arquivo não encontrado: {csv_file_path}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao importar: {e}'))

# class Command(BaseCommand):
#     help = 'Importa lojas do SQL Server usando pyodbc'

#     def handle(self, *args, **kwargs):
#         try:
#             conn_str = (
#                 f"DRIVER=FreeTDS;"
#                 f"SERVER={os.getenv('MSSQL_SERVER')};"
#                 f"PORT={os.getenv('MSSQL_PORT', '1433')};"
#                 f"DATABASE={os.getenv('MSSQL_DATABASE')};"
#                 f"UID={os.getenv('MSSQL_USER')};"
#                 f"PWD={os.getenv('MSSQL_PASSWORD')};"
#                 f"TDS_Version=8.0;"
#             )
#             conn = pyodbc.connect(conn_str)
#             cursor = conn.cursor()
#             cursor.execute("SELECT cod_sucursal, nombre_sucursal FROM dbo.bi_sucursales")

#             count = 0
#             for row in cursor.fetchall():
#                 code, name = row
#                 store, created = Store.objects.update_or_create(
#                     code=code,
#                     defaults={'name': name, 'active': True}
#                 )
#                 count += 1

#             conn.close()
#             self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} lojas importadas/atualizadas.'))

#         except Exception as e:
#             self.stderr.write(self.style.ERROR(f'Erro ao importar: {e}'))
