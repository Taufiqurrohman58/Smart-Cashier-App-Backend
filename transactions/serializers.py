from rest_framework import serializers
from .models import Cart, CartItem, Transaction, TransactionItem
from produks.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'price', 'qty', 'subtotal', 'product_image']

    def get_subtotal(self, obj):
        return obj.subtotal


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']

    def get_total_items(self, obj):
        return obj.total_items

    def get_total_price(self, obj):
        return obj.total_price


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)


class TransactionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = TransactionItem
        fields = ['id', 'product', 'product_name', 'qty', 'price', 'subtotal']


class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(source='transactionitem_set', many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'items', 'total', 'cash_given', 'change', 'payment_method', 'created_at']


class CheckoutSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(min_value=1)
        )
    )
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    cash_given = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=['cash', 'card', 'digital'], default='cash')

    def validate(self, data):
        # Validate that all items exist and calculate change
        items = data['items']
        total = data['total']
        cash_given = data['cash_given']

        if cash_given < total:
            raise serializers.ValidationError("Cash given is less than total amount")

        data['change'] = cash_given - total
        return data