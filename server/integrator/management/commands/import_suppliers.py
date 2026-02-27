import os
import csv
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from suppliers.models import Supplier

load_dotenv()

class Command(BaseCommand):
    help = 'Importa fornecedores de um arquivo CSV localizado na pasta data'

    def handle(self, *args, **kwargs):
        # Define o caminho para o arquivo CSV (mesmo diretório do script)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'data/proveedores.csv')

        try:
            # Abre o arquivo CSV
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader)  # Pula o cabeçalho

                count = 0
                for row in reader:
                    # Extrai apenas as colunas necessárias: cod_proveedor e nombre_proveedor
                    code, name = row[0], row[1]

                    # Converte o código para inteiro e remove espaços extras do nome
                    code = int(code.strip())
                    name = name.strip()

                    # Cria ou atualiza o fornecedor no banco de dados
                    supplier, created = Supplier.objects.update_or_create(
                        code=code,
                        defaults={'name': name, 'active': True}
                    )
                    count += 1

                self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} fornecedores importados/atualizados.'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Arquivo não encontrado: {csv_file_path}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao importar: {e}'))
