from rest_framework import serializers
from suppliers.models import Supplier


class SupplierStoreInputSerializer(serializers.Serializer):
    supplier_code = serializers.IntegerField()
    store_code = serializers.IntegerField()


class SupplierOCResultSerializer(serializers.Serializer):
    supplier_name = serializers.CharField()
    last_open_oc_numbers = serializers.ListField(
        child=serializers.IntegerField()
    )

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
