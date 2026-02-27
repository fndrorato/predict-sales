from django.contrib import admin
from stores.models import Store

admin.site.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'active', 'created_at', 'updated_at')
    list_filter = ('active', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    ordering = ('code', 'name', 'active')
    readonly_fields = ('code', 'name', 'active', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
