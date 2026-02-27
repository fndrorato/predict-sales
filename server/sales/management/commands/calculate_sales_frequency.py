from django.core.management.base import BaseCommand
from django.db.models import Min, Max
from django.db.models.functions import TruncDate
from datetime import timedelta
from items.models import ItemControlStock
from sales.models import Sale

class Command(BaseCommand):
    help = 'Calcula a frequência média de vendas por item e loja e atualiza o campo sales_frequency no modelo ItemControlStock.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando cálculo de frequência de vendas...')

        item_store_pairs = Sale.objects.values('item', 'store') \
            .annotate(first_date=Min('date'), last_date=Max('date'))

        total_updated = 0

        for entry in item_store_pairs:
            item_id = entry['item']
            store_id = entry['store']
            first_date = entry['first_date']
            last_date = entry['last_date']

            if not first_date or not last_date:
                continue

            total_days = (last_date - first_date).days + 1

            distinct_days = Sale.objects.filter(item=item_id, store=store_id) \
                .annotate(sale_day=TruncDate('date')) \
                .values('sale_day') \
                .distinct().count()

            if distinct_days == 0:
                frequency = None
            else:
                frequency = total_days / distinct_days

            try:
                ics = ItemControlStock.objects.get(item_id=item_id, store_id=store_id)
                ics.sales_frequency = round(frequency, 2) if frequency else 0
                ics.save()
                total_updated += 1
            except ItemControlStock.DoesNotExist:
                continue

        self.stdout.write(self.style.SUCCESS(f'Frequência de vendas atualizada para {total_updated} registros.'))
