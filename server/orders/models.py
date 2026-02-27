from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.postgres.fields import ArrayField
from items.models import Item, Section, Subsection
from stores.models import Store
from suppliers.models import Supplier


User = get_user_model()


class OrderSystem(models.Model):
    '''Model com as informações de Ordem de Compra'''
    oc_number = models.BigIntegerField()
    is_open = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.RESTRICT)
    supplier = models.ForeignKey(Supplier, on_delete=models.RESTRICT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField()
    expected_date = models.DateField()   
    received_date = models.DateField(null=True, blank=True) 
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    quantity_order = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    quantity_received = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['oc_number', 'item', 'store'], name='ordersystem_oc_item_store_uniq')
        ]

    def __str__(self):
        return self.item.name
    
    


class OrderSystemResult(models.Model):
    '''Model com as informações de Ordem de Compra'''
    oc_number = models.BigIntegerField()
    store = models.ForeignKey(Store, on_delete=models.RESTRICT)
    supplier = models.ForeignKey(Supplier, on_delete=models.RESTRICT)
    is_open = models.BooleanField(default=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField()
    expected_date = models.DateField()   
    received_date = models.DateField(null=True, blank=True)
    all_items_received = models.SmallIntegerField(default=0)
    received_on_time = models.SmallIntegerField(default=0)
    perfect_order = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.store.name


class OrderStatus(models.Model):
    '''Model com as informações de Ordem de Compra'''
    status = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status


class Order(models.Model):
    '''Model com as informações de Ordem de Compra'''
    supplier = models.ForeignKey(Supplier, on_delete=models.RESTRICT)
    status = models.ForeignKey(OrderStatus, on_delete=models.RESTRICT, default=1)
    store = models.ForeignKey(Store, on_delete=models.RESTRICT)
    date = models.DateField() 
    buyer = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='buyer')
    section = models.ForeignKey(Section, on_delete=models.RESTRICT)
    subsection = models.ForeignKey(Subsection, on_delete=models.RESTRICT, null=True, blank=True)
    sales_date_start = models.DateField(null=True, blank=True)
    sales_date_end = models.DateField(null=True, blank=True)
    # days_stock_desired = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)
    observation = models.TextField(null=True, blank=True)
    oc_numbers_pending = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'


class OrderItem(models.Model):
    '''Model com as informações de Ordem de Compra'''
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    date_last_purchase = models.DateField(null=True, blank=True)
    quantity_last_purchase = models.IntegerField(null=True, blank=True)
    sale_prediction = models.IntegerField(null=True, blank=True)
    stock_available = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, default=0)
    days_stock_desired = models.IntegerField(default=0)
    days_stock_available = models.IntegerField(default=0)
    quantity_suggested = models.IntegerField(null=True, blank=True, default=0)
    quantity_order = models.IntegerField(default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    bonus = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item.name

class OrderLog(models.Model):
    '''Registro de eventos na Ordem de Compra'''
    
    ACTION_CHOICES = [
        ('created', 'Criação'),
        ('status_changed', 'Mudança de Status'),
        ('item_modified', 'Item Modificado'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Se for mudança de status
    previous_status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    new_status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    # Se for modificação de item
    item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    field_changed = models.CharField(max_length=100, null=True, blank=True)
    previous_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)  # observações extras

    def __str__(self):
        return f'{self.order.id} - {self.get_action_display()} - {self.timestamp.strftime("%Y-%m-%d %H:%M")}'

