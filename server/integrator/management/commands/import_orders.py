import csv
import os
from django.core.management.base import BaseCommand
from orders.models import OrderSystem, Store, Supplier
from items.models import Item
from django.utils.dateparse import parse_date


class Command(BaseCommand):
    help = 'Importa ordens de compra a partir de ordens_compra.csv'

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'data/oc_box_2025.csv')        

        if not os.path.exists(file_path):
            self.stderr.write(f'Arquivo CSV não encontrado em: {file_path}')
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            created_count = 0
            updated_count = 0

            for row in reader:
                try:
                    store = Store.objects.get(code=int(row['sucursal']))
                    supplier = Supplier.objects.get(code=int(row['cod_proveedor']))
                    item = Item.objects.get(code=str(row['codigo']).replace('"', '').strip())

                    oc_number = int(float(row['nro_pedido']))

                    order, created = OrderSystem.objects.update_or_create(
                        oc_number=oc_number,
                        item=item,
                        defaults={
                            'store': store,
                            'supplier': supplier,
                            'total_amount': float(row['importe']),
                            'is_open': bool(int(row['abierta'])),
                            'date': parse_date(row['fecha'].split(' ')[0]),
                            'expected_date': parse_date(row['fecha_prevista'].split(' ')[0]),
                            'received_date': parse_date(row['fecha_recepcion'].split(' ')[0]) if row['fecha_recepcion'] else None,
                            'quantity_order': float(row['cantidad_ped']),
                            'quantity_received': float(row['cantidad_recep']),
                            'price': float(row['precio']),
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                except Store.DoesNotExist:
                    self.stderr.write(f"Loja com código {row['sucursal']} não encontrada.")
                except Supplier.DoesNotExist:
                    self.stderr.write(f"Fornecedor com código {row['cod_proveedor']} não encontrado.")
                except Item.DoesNotExist:
                    self.stderr.write(f"Item com código {row['codigo']} não encontrado.")
                except Exception as e:
                    self.stderr.write(f"Erro na linha {row}: {str(e)}")

            self.stdout.write(self.style.SUCCESS(f'{created_count} ordens criadas, {updated_count} ordens atualizadas com sucesso.'))
