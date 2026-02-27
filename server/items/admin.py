from django.contrib import admin
from items.models import Item, ItemControlStock, Section, Subsection


class ItemControlStockInline(admin.TabularInline):
    model = ItemControlStock
    extra = 1
    fields = ('store', 'days_stock', 'stock_min', 'stock_max', 'stock_available', 'stock_available_on')
    show_change_link = True


class ItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'section', 'brand', 'purchase_price', 'cost_price', 'sale_price', 'supplier', 'is_disabled')
    search_fields = ('code', 'name', 'section', 'subsection', 'brand')
    list_filter = ('is_disabled', 'supplier', 'section', 'subsection')
    ordering = ('name',)
    inlines = [ItemControlStockInline]


class ItemControlStockAdmin(admin.ModelAdmin):
    list_display = ('item', 'store', 'days_stock', 'stock_min', 'stock_max', 'stock_available', 'stock_available_on')
    search_fields = ('item__name', 'store__name')
    list_filter = ('store',)
    ordering = ('store',)


class SectionAdmin(admin.ModelAdmin):
    model = Section
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

class SubsectionAdmin(admin.ModelAdmin):
    model = Subsection
    list_display = ('name', 'section')
    search_fields = ('name', 'section__name')
    ordering = ('name',)

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemControlStock, ItemControlStockAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Subsection, SubsectionAdmin)
