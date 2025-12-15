from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    kasir = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'deskripsi', 'jumlah', 'tanggal', 'kasir']
        read_only_fields = ['id', 'tanggal', 'kasir']


class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['deskripsi', 'jumlah']