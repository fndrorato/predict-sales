from django.core.management.base import BaseCommand
from django.db.models import F
from orders.models import OrderSystem, OrderSystemResult


class Command(BaseCommand):
    help = 'Gera ou atualiza resumos para cada Ordem de Compra (OrderSystemResult)'

    def handle(self, *args, **kwargs):
        oc_numbers = OrderSystem.objects.values_list('oc_number', flat=True).distinct()
        total = 0

        for oc_number in oc_numbers:
            result = self.gerar_resumo_oc(oc_number)
            total += 1
            self.stdout.write(f"[✔] Resumo gerado para OC {oc_number}")

        self.stdout.write(self.style.SUCCESS(f"✔ {total} resumos gerados/atualizados."))

    def gerar_resumo_oc(self, oc_number):
        orders = OrderSystem.objects.filter(oc_number=oc_number)

        if not orders.exists():
            return None

        first = orders.first()

        total_amount = sum([
            (o.price or 0) * o.quantity_order
            for o in orders
        ])

        all_items_received = int(all([
            o.quantity_order == o.quantity_received
            for o in orders
        ]))

        received_on_time = int(all([
            o.received_date and o.received_date <= o.expected_date
            for o in orders
        ]))

        perfect_order = all_items_received * received_on_time

        obj, created = OrderSystemResult.objects.update_or_create(
            oc_number=oc_number,
            defaults={
                'store': first.store,
                'supplier': first.supplier,
                'is_open': first.is_open,
                'date': first.date,
                'expected_date': first.expected_date,
                'received_date': first.received_date,
                'total_amount': total_amount,
                'all_items_received': all_items_received,
                'received_on_time': received_on_time,
                'perfect_order': perfect_order,
            }
        )

        return obj
