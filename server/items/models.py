from django.db import models
from suppliers.models import Supplier
from stores.models import Store


class Item(models.Model):
    code = models.CharField(max_length=14, primary_key=True)
    name = models.CharField(max_length=50)
    pack_size = models.DecimalField(max_digits=9, null=True, blank=True, decimal_places=2)
    min_size = models.IntegerField(null=True, blank=True)
    unit_of_measure = models.CharField(max_length=10, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True)
    section = models.CharField(max_length=35, null=True, blank=True)
    subsection = models.CharField(max_length=35, null=True, blank=True)
    nivel3 = models.CharField(max_length=35, null=True, blank=True)
    nivel4 = models.CharField(max_length=35, null=True, blank=True)
    nivel5 = models.CharField(max_length=35, null=True, blank=True)
    brand = models.CharField(max_length=35, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True)
    is_disabled_purchase = models.BooleanField(default=True)
    is_disabled = models.BooleanField(default=True)
    matriz_price = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.RESTRICT)
    ean = models.CharField(max_length=28, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ItemControlStock(models.Model):
    item = models.ForeignKey(
        Item, 
        on_delete=models.RESTRICT,
        to_field='code'
    )
    store = models.ForeignKey(
        Store, 
        on_delete=models.RESTRICT,
        to_field='code'
    )    
    days_stock = models.IntegerField(default=0)
    stock_min = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    stock_max = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    stock_available = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    stock_available_on = models.DateField(null=True, blank=True)
    date_last_purchase = models.DateField(null=True, blank=True)
    sales_frequency = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, default=0)
    quantity_last_purchase = models.DecimalField(max_digits=9, decimal_places=2, default=0)    

    class Meta:
        unique_together = (('item', 'store'),) 

    def __str__(self):
        return self.item.name

class Section(models.Model):
    '''Model com as informações de Seção  de Produtos'''
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Subsection(models.Model):
    '''Model com as informações de Seção  de Produtos'''
    name = models.CharField(max_length=50)
    section = models.ForeignKey(Section, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ItemGroupView(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    section = models.CharField(max_length=255)
    subsection = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'sales_item_group_view'
        verbose_name = 'Item Group View'
        verbose_name_plural = 'Item Group Views'
