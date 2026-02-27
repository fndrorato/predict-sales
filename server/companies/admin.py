from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'state', 'website')
    search_fields = ('name', 'email', 'phone', 'city', 'state')
    list_filter = ('state', 'city')
