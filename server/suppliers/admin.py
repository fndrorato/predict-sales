from django.contrib import admin
from suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'active', 'created_at', 'updated_at')
    list_filter = ('active',)
    search_fields = ('name', 'code')
    ordering = ('code',)

