from django.core.management.base import BaseCommand
from items.models import Item, Section, Subsection


class Command(BaseCommand):
    help = 'Importa sections e subsections distintos a partir dos dados do modelo Item'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando importação de sections e subsections..."))

        # Step 1: Importar sections distintos
        sections = Item.objects.exclude(section__isnull=True).exclude(section__exact='') \
                               .values_list('section', flat=True).distinct()

        for section_name in sections:
            section, created = Section.objects.get_or_create(name=section_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Section criada: {section_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Section já existe: {section_name}"))

            # Step 2: Importar subsections para a section
            subsections = Item.objects.filter(section=section_name) \
                                      .exclude(subsection__isnull=True).exclude(subsection__exact='') \
                                      .values_list('subsection', flat=True).distinct()

            for subsection_name in subsections:
                sub_created = Subsection.objects.get_or_create(name=subsection_name, section=section)
                if sub_created[1]:
                    self.stdout.write(self.style.SUCCESS(f"  Subsection criada: {subsection_name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Subsection já existe: {subsection_name}"))

        self.stdout.write(self.style.SUCCESS("Importação concluída com sucesso."))
