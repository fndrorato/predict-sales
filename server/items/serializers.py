from rest_framework import serializers
from items.models import Item, ItemControlStock, Section, Subsection


class ItemControlStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemControlStock
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    item_control_stock = ItemControlStockSerializer(source='itemcontrolstock_set', many=True)

    class Meta:
        model = Item
        fields = '__all__'

class SubsectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsection
        fields = ['id', 'name']


class SectionSerializer(serializers.ModelSerializer):
    subsections = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'name', 'subsections']

    def get_subsections(self, obj):
        subsections = Subsection.objects.filter(section=obj)
        return SubsectionSerializer(subsections, many=True).data

class ItemViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class ItemControlStockErrorSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='item.code')
    name = serializers.CharField(source='item.name')
    supplier = serializers.StringRelatedField(source='item.supplier')
    brand = serializers.CharField(source='item.brand')
    section = serializers.CharField(source='item.section')
    subsection = serializers.CharField(source='item.subsection')
    nivel3 = serializers.CharField(source='item.nivel3')
    nivel4 = serializers.CharField(source='item.nivel4')
    nivel5 = serializers.CharField(source='item.nivel5')
    store = serializers.CharField(source='store.name')
    cost_price = serializers.DecimalField(source='item.cost_price', max_digits=13, decimal_places=0)
    
    class Meta:
        model = ItemControlStock
        fields = [
            'code',
            'name',
            'supplier',
            'brand',
            'section',
            'subsection',
            'nivel3',
            'nivel4',
            'nivel5',
            'store',
            'cost_price',
            'stock_available',
            'stock_available_on',
        ]
