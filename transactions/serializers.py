from rest_framework import serializers
from .models import Transaction, TransactionItem


class PaymentSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField()
    )
    uang_bayar = serializers.IntegerField(min_value=1)


class HistoryItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    qty = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class HistorySerializer(serializers.Serializer):
    invoice = serializers.CharField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    uang_bayar = serializers.DecimalField(max_digits=10, decimal_places=2)
    kembalian = serializers.DecimalField(max_digits=10, decimal_places=2)
    kasir = serializers.CharField()
    created_at = serializers.CharField()
    items = HistoryItemSerializer(many=True)
