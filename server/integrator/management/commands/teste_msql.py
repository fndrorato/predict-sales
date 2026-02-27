from django.core.management.base import BaseCommand
import pyodbc

class Command(BaseCommand):
    help = 'Testa a conexão com o banco de dados SQL Server'

    def handle(self, *args, **kwargs):
        conn_str = (
            "DRIVER={FreeTDS};"
            "SERVER=192.168.30.8;"
            "PORT=1433;"
            "DATABASE=pegasus;"
            "UID=consulta;"
            "PWD=123consulta;"
            "TDS_Version=8.0;"
        )

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("Conexão bem-sucedida!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro na conexão: {e}"))