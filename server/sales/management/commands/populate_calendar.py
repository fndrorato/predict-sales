from django.core.management.base import BaseCommand
from datetime import date, timedelta
from sales.models import Calendar  # substitua pelo nome real do seu app

class Command(BaseCommand):
    help = 'Popula o modelo Calendar com datas de 2023-01-01 até 2039-12-31'

    def handle(self, *args, **kwargs):
        inicio = date(2023, 1, 1)
        fim = date(2039, 12, 31)
        delta = timedelta(days=1)

        data = inicio
        criados = 0
        while data <= fim:
            obj, created = Calendar.objects.get_or_create(date=data)
            if created:
                criados += 1
            data += delta

        self.stdout.write(self.style.SUCCESS(f'{criados} datas adicionadas com sucesso ao Calendar.'))
