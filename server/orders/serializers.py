import locale
from datetime import date
from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from items.models import Item, Section
from orders.models import OrderSystem, Order, OrderItem, OrderStatus, OrderLog
from stores.models import Store
from stores.serializers import StoreSerializer
from suppliers.models import Supplier
from items.serializers import SectionSerializer
from notifications.models import Notification



locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class OrderStartDefaultSerializer(serializers.Serializer):
    stores = StoreSerializer(many=True)
    sections = SectionSerializer(many=True)


class OrderSystemItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name')
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderSystem
        fields = ['item', 'item_name', 'quantity_order', 'quantity_received', 'price']

    def get_price(self, obj):
        if obj.price is not None:
            return locale.format_string("%.0f", obj.price, grouping=True).replace(',', '.')
        return None

class OrderSystemGroupedSerializer(serializers.Serializer):
    oc_number = serializers.IntegerField()
    store = serializers.IntegerField()
    store_name = serializers.CharField()
    supplier = serializers.IntegerField()
    supplier_name = serializers.CharField()
    total_amount = serializers.SerializerMethodField()
    date = serializers.DateField()
    expected_date = serializers.DateField()
    items = OrderSystemItemSerializer(many=True)

    def get_total_amount(self, obj):
        print(obj.total_amount)
        if obj.total_amount is not None:
            return locale.format_string("%.2f", obj.total_amount, grouping=True).replace(',', '.')
        return None

class OrderDetailStockSerializer(serializers.Serializer):
    item_code = serializers.CharField(max_length=14)
    item_name = serializers.CharField(max_length=50)
    pack_size = serializers.DecimalField(max_digits=9, decimal_places=2, default=0)
    stock_available = serializers.DecimalField(max_digits=9, decimal_places=2, default=0)
    date_last_purchase = serializers.DateField(format='%d/%m/%Y', required=False, allow_null=True)
    cost_price = serializers.DecimalField(max_digits=13, decimal_places=2, required=False, allow_null=True)
    purchase_price = serializers.DecimalField(max_digits=13, decimal_places=0, required=False, allow_null=True)
    quantity_last_purchase = serializers.DecimalField(max_digits=9, decimal_places=2, required=False, allow_null=True)
    quantity_suggested = serializers.DecimalField(max_digits=9, decimal_places=2, default=0)
    current_stock_days = serializers.IntegerField(default=0)
    days_stock = serializers.IntegerField(default=0)
    sale_prediction = serializers.DecimalField(max_digits=9, decimal_places=2, default=0)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if data.get('date_last_purchase') is None:
            data['quantity_last_purchase'] = None

        return data

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    item_pack_size = serializers.SerializerMethodField()
    date_last_purchase = serializers.DateField(
        required=False,
        allow_null=True,
        format='%d/%m/%Y'  # <-- só afeta o GET
    )


    class Meta:
        model = OrderItem
        fields = [
            'id', 'item', 'item_name', 'item_pack_size', 'date_last_purchase', 
            'quantity_last_purchase', 'sale_prediction', 'days_stock_desired',
            'quantity_suggested', 'quantity_order', 'bonus', 'discount', 'price', 
            'stock_available', 'days_stock_available', 'price', 'total_amount', 
        ]

    def get_item_name(self, obj):
        return obj.item.name if obj.item else None

    def get_item_pack_size(self, obj):
        return obj.item.pack_size if obj.item and hasattr(obj.item, 'pack_size') else None    
    
    # def get_date_last_purchase(self, obj):
    #     if obj.date_last_purchase:
    #         return obj.date_last_purchase.strftime('%d/%m/%Y')
        return None

    def validate_item(self, value):
        if not value:
            raise serializers.ValidationError("Item é obrigatório.")
        return value

    def validate(self, data):
        for field in ['quantity_order', 'bonus', 'discount']:
            if data.get(field, 0) < 0:
                raise serializers.ValidationError(f"{field} não pode ser menor que 0.")
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)  # <-- para retornar no GET
    items_data = OrderItemSerializer(many=True, write_only=True, source='items')  # <-- para receber no POST/PUT

    supplier_name = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    
    status_id = serializers.IntegerField(source='status.id', read_only=True)
    status_name = serializers.CharField(source='status.status', read_only=True)    

    class Meta:
        model = Order
        fields = [
            'id', 'supplier', 'supplier_name',
            'store', 'store_name', 'section', 'subsection', 
            'sales_date_start', 'sales_date_end',
            'total_amount', 'observation', 'oc_numbers_pending', 
            'status_id', 'status_name',
            'items', 'items_data',
        ]
        
    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else None

    def get_store_name(self, obj):
        return obj.store.name if obj.store else None

    def validate(self, data):
        errors = {}
        today = date.today()

        if not data.get('supplier'):
            errors['supplier'] = "Fornecedor é obrigatório."

        if not data.get('store'):
            errors['store'] = "Loja é obrigatória."

        if not data.get('section'):
            errors['section'] = "Seção é obrigatória."

        s_start = data.get('sales_date_start')
        s_end = data.get('sales_date_end')

        if not s_start or not s_end:
            errors['sales_date_start'] = "Datas de venda são obrigatórias."
        else:
            if s_start < today:
                errors['sales_date_start'] = "Data de início de venda deve ser a partir de hoje."
            if s_end <= s_start:
                errors['sales_date_end'] = "Data de fim de venda deve ser maior que início."

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user
        user_groups = {g.name.lower() for g in user.groups.all()}
        status = instance.status.id

        # Bloqueia edição se status for 3
        if status == 3:
            raise PermissionDenied("Ordem com status 3 não pode ser alterada.")

        # Comprador só pode editar status 1
        if 'comprador' in user_groups and status != 1:
            raise PermissionDenied("Compradores só podem editar ordens com status 1.")

        # Analista pode editar status 1 ou 2, mas não 3 (já tratado acima)
        if 'analista' in user_groups and status not in [1, 2]:
            raise PermissionDenied("Analistas só podem editar ordens com status 1 ou 2.")

        # Supervisor pode editar status 1 ou 2
        if 'supervisor' in user_groups and status not in [1, 2]:
            raise PermissionDenied("Supervisores só podem editar ordens com status 1 ou 2.")

        old_status = instance.status
        
        items_data = validated_data.pop('items', [])        

        # Atualiza os campos da Order      
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Log de mudança de status   
        new_status = instance.status 
        if old_status != new_status:
            OrderLog.objects.create(
                order=instance,
                action='status_changed',
                user=request.user,
                previous_status=old_status,
                new_status=new_status,
                notes='Status alterado'
            )
            if old_status.id == 2 and new_status.id in [3, 4] and 'supervisor' in user_groups:
                Notification.objects.create(
                    user=instance.buyer,
                    title="Status da OC Atualizado",
                    message=f"Sua OC #{instance.id} foi {'aprovada' if new_status.id == 3 else 'recusada'} pelo supervisor.",
                    type="success" if new_status.id == 3 else "error",
                    link=f"/ordens-compra/{instance.id}/"
                )
            

        # Se foi um comprador que aprovou (de status 1 para 2), notifica supervisores
        if old_status.id == 1 and new_status.id == 2 and 'comprador' in user_groups:
            supervisores = User.objects.filter(groups__name="supervisor")
            for user in supervisores:
                Notification.objects.create(
                    user=user,
                    title="Ordem aguardando aprovação final",
                    message=f"A OC #{instance.id} foi aprovada pelo comprador e aguarda sua aprovação.",
                    type="warning",
                    link=f"/ordens-compra/{instance.id}/"
                )
        
        # Mapeia os itens atuais da Order pelo item.code
        existing_items = {oi.item.code: oi for oi in instance.items.all()}
        incoming_item_codes = []

        for item_data in items_data:
            # item pode vir como string (code) ou objeto
            item_code = item_data['item'].code if hasattr(item_data['item'], 'code') else item_data['item']
            incoming_item_codes.append(item_code)

            if item_code in existing_items:
                order_item = existing_items[item_code]

                for attr, value in item_data.items():
                    if hasattr(order_item, attr):
                        old_value = getattr(order_item, attr, None)
                        if old_value != value:
                            OrderLog.objects.create(
                                order=instance,
                                action='item_modified',
                                user=self.context['request'].user,
                                item=order_item,
                                field_changed=attr,
                                previous_value=str(old_value),
                                new_value=str(value),
                                notes=f'Modificação no item {order_item.item.code}'
                            )
                        setattr(order_item, attr, value)

                order_item.save()

        # Remove itens que não vieram mais na atualização
        instance.items.exclude(item__code__in=incoming_item_codes).delete()

        return instance

class OrderPendingSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    buyer_name = serializers.SerializerMethodField()
    section_name = serializers.CharField(source='section.name', read_only=True)
    status_name = serializers.CharField(source='status.status', read_only=True, default=None)
    store_name = serializers.CharField(source='store.name', read_only=True, default=None)
    subsection_name = serializers.CharField(source='subsection.name', read_only=True, default=None)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'supplier', 'supplier_name',
            'status', 'status_name',
            'store', 'store_name',
            'date', 'buyer', 'buyer_name',
            'section', 'section_name',
            'subsection', 'subsection_name',
            'sales_date_start', 'sales_date_end',
            'total_amount',
        ]

    def get_buyer_name(self, obj):
        first_name = obj.buyer.first_name or ''
        last_name = obj.buyer.last_name or ''
        full_name = f'{first_name} {last_name}'.strip()
        return full_name if full_name else obj.buyer.username

    def get_total_amount(self, obj):
        return float(obj.total_amount) if obj.total_amount is not None else 0.0

class OrderBulkUpdateStatusSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

class OrderLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    item_name = serializers.CharField(source='item.item.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = OrderLog
        fields = [
            'id', 'order', 'action', 'action_display', 'user_name', 'timestamp',
            'previous_status', 'new_status',
            'item', 'item_name', 'field_changed',
            'previous_value', 'new_value', 'notes'
        ]

