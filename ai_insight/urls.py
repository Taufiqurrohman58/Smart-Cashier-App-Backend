from django.urls import path
from .views import (
    insight_penjualan,
    rekomendasi_stok,
    prediksi_barang_habis
)

urlpatterns = [
    path('ai/insight-penjualan/', insight_penjualan),
    path('ai/rekomendasi-stok/', rekomendasi_stok),
    path('ai/prediksi-habis/', prediksi_barang_habis),
]
