import os
import pandas as pd
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Max
from items.models import Item, ItemControlStock
from stores.models import Store
from orders.models import OrderSystem 


class Command(BaseCommand):
    help = 'Importa os dados de estoque de um arquivo CSV'

    def handle(self, *args, **options):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, 'data/stock.csv')

        if not os.path.exists(csv_file_path):
            self.stderr.write(f'Arquivo CSV não encontrado em: {csv_file_path}')
            return

        # Carregar o CSV com pandas
        df = pd.read_csv(csv_file_path, delimiter=";")

        # Agrupar por 'codigo' (item) e 'cod_sucursal' (store)
        df_grouped = df.groupby(['codigo', 'cod_sucursal'])['cantidad'].sum().reset_index()

        count = 0
        for _, row in df_grouped.iterrows():
            item_code = str(int(row['codigo']))
            store_code = str(int(row['cod_sucursal']))
            stock_qty = Decimal(row['cantidad'])

            try:
                # Buscar item e store
                item = Item.objects.get(code=item_code)
                store = Store.objects.get(code=store_code)

                # Obter a última compra de OrderSystem onde quantity_received > 0
                last_purchase = OrderSystem.objects.filter(
                    item=item,
                    store=store,
                    quantity_received__gt=0
                ).aggregate(last_received_date=Max('received_date'))

                # Preparar as variáveis para gravar no ItemControlStock
                date_last_purchase = last_purchase['last_received_date'] if last_purchase['last_received_date'] else None
                quantity_last_purchase = 0  # Pode ser alterado caso precise da quantidade da última compra
                if date_last_purchase:
                    last_order = OrderSystem.objects.filter(
                        item=item,
                        store=store,
                        received_date=date_last_purchase
                    ).first()
                    if last_order:
                        quantity_last_purchase = last_order.quantity_received

                # Criar ou atualizar o controle de estoque
                ItemControlStock.objects.update_or_create(
                    item=item,
                    store=store,
                    defaults={
                        'stock_available': stock_qty,
                        'stock_available_on': pd.to_datetime('today').date(),
                        'date_last_purchase': date_last_purchase,
                        'quantity_last_purchase': quantity_last_purchase
                    }
                )
                count += 1
            except Item.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Item com código {item_code} não encontrado.'))
            except Store.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Store com código {store_code} não encontrado.'))

        self.stdout.write(self.style.SUCCESS(f'{count} registros processados com sucesso.'))
