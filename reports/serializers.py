from rest_framework import serializers


class ReportItemSerializer(serializers.Serializer):
    produk = serializers.CharField()
    qty = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)


class ReportTransactionSerializer(serializers.Serializer):
    invoice = serializers.CharField()
    kasir = serializers.CharField()
    items = ReportItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class ReportExpenseSerializer(serializers.Serializer):
    deskripsi = serializers.CharField()
    jumlah = serializers.DecimalField(max_digits=12, decimal_places=2)
    kasir = serializers.CharField()
