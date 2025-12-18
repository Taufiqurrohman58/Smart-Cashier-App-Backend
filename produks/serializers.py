from rest_framework import serializers
from .models import GudangProduct, KantinProduct


class GudangProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = GudangProduct
        fields = ['id', 'name', 'category', 'price', 'stock_gudang', 'satuan', 'image', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class KantinProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product_gudang.name', read_only=True)
    price = serializers.DecimalField(source='product_gudang.price', max_digits=10, decimal_places=2, read_only=True)
    image = serializers.ImageField(source='product_gudang.image', read_only=True)
    satuan = serializers.CharField(source='product_gudang.satuan', read_only=True)
    category = serializers.CharField(source='product_gudang.category', read_only=True)

    class Meta:
        model = KantinProduct
        fields = ['id', 'product_gudang', 'name', 'category', 'price', 'stock_kantin', 'satuan', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransferStokSerializer(serializers.Serializer):
    product_gudang_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class TambahStokGudangSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class TransferResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    product = serializers.SerializerMethodField()

    def get_product(self, obj):
        gudang_product = obj['gudang_product']
        kantin_product = obj.get('kantin_product')
        return {
            'id': gudang_product.id,
            'name': gudang_product.name,
            'stock_gudang': gudang_product.stock_gudang,
            'stock_kantin': kantin_product.stock_kantin if kantin_product else 0
        }


class TambahStokGudangResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    product = serializers.SerializerMethodField()

    def get_product(self, obj):
        product = obj['product']
        return {
            'id': product.id,
            'name': product.name,
            'stock_gudang': product.stock_gudang
        }