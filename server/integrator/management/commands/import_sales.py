import csv
import os
from django.core.management.base import BaseCommand
from items.models import Item
from sales.models import Sale
from stores.models import Store
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'Importa vendas de um arquivo CSV para o modelo Sale usando bulk_create'

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(current_dir, 'data/ventas_hasta_2025_08_17.csv')        

        if not os.path.exists(csv_file):
            self.stderr.write(f'Arquivo CSV não encontrado em: {csv_file}')
            return

        # Cache de lojas e itens
        store_map = {store.code: store for store in Store.objects.all()}
        item_map = {item.code: item for item in Item.objects.all()}

        sales_to_create = []
        batch_size = 1000
        total = 0
        skipped = 0

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')

            for row in reader:
                try:
                    ticket_number = row['nro_factura'].strip().strip('"')
                    date = datetime.strptime(row['fecha'], "%Y-%m-%d %H:%M:%S.%f").date()
                    time = int(row['hora'])
                    store_code = int(row['cod_sucursal'])
                    item_code = row['codigo']
                    quantity = int(float(row['cant_vta'].replace(',', '.')))
                    price = Decimal(row['ventas_det_precio_neto'].replace('"', '').replace(',', '.'))

                    store = store_map.get(store_code)
                    item = item_map.get(item_code)

                    if not store or not item:
                        skipped += 1
                        continue

                    sales_to_create.append(Sale(
                        ticket_number=ticket_number,
                        store=store,
                        date=date,
                        time=time,
                        item=item,
                        quantity=quantity,
                        price=price
                    ))

                    if len(sales_to_create) >= batch_size:
                        Sale.objects.bulk_create(sales_to_create, batch_size=batch_size)
                        total += len(sales_to_create)
                        sales_to_create = []

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro na linha {row}: {e}"))
                    skipped += 1

        # Inserir o restante
        if sales_to_create:
            Sale.objects.bulk_create(sales_to_create, batch_size=batch_size)
            total += len(sales_to_create)

        self.stdout.write(self.style.SUCCESS(f"Importação concluída: {total} vendas inseridas. {skipped} linhas ignoradas."))
