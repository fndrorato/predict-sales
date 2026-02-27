import os
import csv
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from suppliers.models import Supplier
from items.models import Item

load_dotenv()


class Command(BaseCommand):
    help = 'Importa itens de um arquivo CSV localizado na pasta data'

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'data/productos.csv')

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader)  # Pula o cabeçalho

                count = 0
                for line_number, row in enumerate(reader, start=2):
                    try:
                        code = row[0].strip()

                        # Valida se começa com número
                        if not code or not code[0].isdigit():
                            self.stderr.write(self.style.WARNING(f'Linha {line_number} ignorada: código inválido "{code}"'))
                            continue

                        item_data = {
                            'name': row[1].strip(),
                            'pack_size': float(row[2].strip()) if row[2].strip() else None,
                            'min_size': int(row[3].strip()) if row[3].strip() else None,
                            'unit_of_measure': row[4].strip(),
                            'purchase_price': float(row[5].strip()) if row[5].strip() else None,
                            'cost_price': float(row[6].strip()) if row[6].strip() else None,
                            'section': row[10].strip(),
                            'subsection': row[11].strip(),
                            'nivel3': row[12].strip(),
                            'nivel4': row[13].strip(),
                            'nivel5': row[14].strip(),
                            'brand': row[15].strip(),
                            'sale_price': float(row[16].strip()) if row[16].strip() else None,
                            'ean': row[17].strip() if len(row) > 17 else None,
                            'is_disabled_purchase': bool(int(row[18].strip())) if row[18].strip() else False,
                            'is_disabled': bool(int(row[20].strip())) if row[20].strip() else False,
                            'matriz_price': float(row[42].strip()) if len(row) > 43 and row[43].strip() else None,
                        }

                        supplier_code = row[40].strip()
                        supplier_name = row[41].strip()
                        print(f'Code:{code} - Supplier Code: {supplier_code} - Supplier Name: {supplier_name}') 
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
                        self.stderr.write(self.style.ERROR(f'Erro na linha {line_number}: {e}'))

                self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} itens importados/atualizados.'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Arquivo não encontrado: {csv_file_path}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao importar: {e}'))
