from django.contrib import admin
from .models import OrderStatus, Order

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('status',)
    ordering = ('status',)
    list_per_page = 20

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'status', 'store', 'date', 'buyer', 'section', 'sales_date_range')
    list_filter = ('status', 'store', 'section', 'date', 'buyer')
    search_fields = ('supplier__name', 'observation', 'buyer__username')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    list_per_page = 30
    raw_id_fields = ('supplier', 'buyer')  # Useful if you have many suppliers/users
    autocomplete_fields = ('subsection',)  # Requires the model to be registered with search_fields
    
    fieldsets = (
        (None, {
            'fields': ('supplier', 'status', 'store', 'date', 'buyer')
        }),
        ('Section Information', {
            'fields': ('section', 'subsection')
        }),
        ('Sales Dates', {
            'fields': ('sales_date_start', 'sales_date_end'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('observation',),
            'classes': ('wide',)
        }),
    )
    
    def sales_date_range(self, obj):
        if obj.sales_date_start and obj.sales_date_end:
            return f"{obj.sales_date_start} to {obj.sales_date_end}"
        return "-"
    sales_date_range.short_description = 'Sales Date Range'