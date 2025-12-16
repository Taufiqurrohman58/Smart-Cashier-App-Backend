from rest_framework import serializers

class InsightPenjualanSerializer(serializers.Serializer):
    produk = serializers.CharField()
    total_terjual = serializers.IntegerField()
    total_pendapatan = serializers.DecimalField(max_digits=12, decimal_places=2)

class RekomendasiStokSerializer(serializers.Serializer):
    produk = serializers.CharField()
    stok_sekarang = serializers.IntegerField()
    saran_stok = serializers.IntegerField()
    alasan = serializers.CharField()

class PrediksiHabisSerializer(serializers.Serializer):
    produk = serializers.CharField()
    stok_sekarang = serializers.IntegerField()
    estimasi_habis_hari = serializers.IntegerField()
    status = serializers.CharField()
