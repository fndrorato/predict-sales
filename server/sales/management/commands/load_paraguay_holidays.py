import holidays
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from sales.models import Calendar


IMPORTANT_KEYWORDS_ES = {
    # ajuste à sua preferência; estes são os mais comuns em varejo
    "Año Nuevo",
    "Día de los Héroes",
    "Jueves Santo",
    "Viernes Santo",
    "Pascua",               # às vezes aparece “Resurrección”
    "Día del Trabajador",
    "Independencia",
    "Chaco",                # Paz del Chaco
    "Fundación de Asunción",
    "Asunción",             # alguns nomes variam
    "Virgen de Caacupé",
    "Navidad",
}
IMPORTANT_KEYWORDS_PT = {
    "Ano Novo",
    "Dia dos Heróis",
    "Quinta-feira Santa",
    "Sexta-feira Santa",
    "Páscoa",
    "Dia do Trabalhador",
    "Independência",
    "Chaco",               # Paz do Chaco
    "Fundação de Assunção",
    "Assunção",
    "Virgem de Caacupé",
    "Natal",
}

class Command(BaseCommand):
    help = "Carrega/atualiza feriados do Paraguai no model Calendar"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-year", type=int, required=True,
            help="Ano inicial (ex.: 2023)"
        )
        parser.add_argument(
            "--end-year", type=int, required=True,
            help="Ano final (ex.: 2026)"
        )
        parser.add_argument(
            "--only-important", action="store_true",
            help="Se definido, grava somente feriados considerados 'importantes' para varejo"
        )
        parser.add_argument(
            "--language", choices=["es", "pt"], default="es",
            help="Idioma do nome do feriado salvo (es ou pt). Padrão: es"
        )

    def handle(self, *args, **options):
        start_year = options["start_year"]
        end_year = options["end_year"]
        only_important = options["only_important"]
        language = options["language"]

        # holidays.Paraguay suporta idioma "es"
        # Para "pt", usamos uma pequena tradução/mapeamento simples (fallback).
        if language == "es":
            py_holidays = holidays.Paraguay(years=range(start_year, end_year + 1), language="es")
            important_set = IMPORTANT_KEYWORDS_ES
        else:
            # Não há locale oficial "pt" para PY na lib; usaremos "es" e um mapeamento simples.
            py_holidays = holidays.Paraguay(years=range(start_year, end_year + 1), language="es")
            important_set = IMPORTANT_KEYWORDS_PT

        def translate_to_pt(name_es: str) -> str:
            # mapeamento básico (opcionalmente expanda conforme sua necessidade)
            replacements = {
                "Año Nuevo": "Ano Novo",
                "Día de los Héroes": "Dia dos Heróis",
                "Jueves Santo": "Quinta-feira Santa",
                "Viernes Santo": "Sexta-feira Santa",
                "Pascua": "Páscoa",
                "Día del Trabajador": "Dia do Trabalhador",
                "Independencia": "Independência",
                "Paz del Chaco": "Paz do Chaco",
                "Fundación de Asunción": "Fundação de Assunção",
                "Virgen de Caacupé": "Virgem de Caacupé",
                "Navidad": "Natal",
            }
            for k, v in replacements.items():
                if k in name_es:
                    return name_es.replace(k, v)
            return name_es  # fallback

        created, updated = 0, 0

        with transaction.atomic():
            for dt, name_es in py_holidays.items():
                # Filtrar apenas “importantes” se solicitado
                if only_important:
                    base_name = name_es
                    check_set = important_set
                    # usaremos o nome em ES para decidir “importância”
                    if not any(key.lower() in base_name.lower() for key in check_set):
                        continue

                # idioma final
                holiday_name = name_es if language == "es" else translate_to_pt(name_es)

                obj, was_created = Calendar.objects.update_or_create(
                    date=dt,
                    defaults={
                        "is_holiday": True,
                        "holiday_name": holiday_name,
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {created} criados, {updated} atualizados "
                f"({start_year}–{end_year}, idioma={language}, only_important={only_important})"
            )
        )
