import csv
import os
from django.core.management.base import BaseCommand
from items.models import Item, ItemControlStock
from stores.models import Store
from django.db import transaction

class Command(BaseCommand):
    help = 'Importa dados do controle de estoque a partir de um CSV e mostra os fornecedores únicos dos itens processados'

    @transaction.atomic
    def handle(self, *args, **options):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'data/rotacion_stock.csv')        

        # Armazena os supplier_ids únicos
        supplier_ids = set()

        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                try:
                    item_code = int(row['code'].strip())
                    store_code = int(row['sucursal'].strip())
                    days_stock = int(row['rotacion'].strip())

                    item = Item.objects.get(code=item_code)
                    store = Store.objects.get(code=store_code)

                    obj, created = ItemControlStock.objects.update_or_create(
                        item=item,
                        store=store,
                        defaults={'days_stock': days_stock}
                    )

                    supplier_ids.add(item.supplier_id)  # Coleta fornecedor

                    status = "Criado" if created else "Atualizado"
                    self.stdout.write(f"{status}: item={item_code}, store={store_code}, days_stock={days_stock}")

                except Item.DoesNotExist:
                    self.stderr.write(f"Item não encontrado: code={row['code']}")
                except Store.DoesNotExist:
                    self.stderr.write(f"Store não encontrada: sucursal={row['sucursal']}")
                except Exception as e:
                    self.stderr.write(f"Erro ao processar linha {row}: {str(e)}")

        # Exibe os fornecedores únicos
        self.stdout.write("\nFornecedores únicos dos itens processados:")
        for sid in sorted(supplier_ids):
            self.stdout.write(f"Fornecedor ID: {sid}")
