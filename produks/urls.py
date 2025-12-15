from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GudangProductViewSet, KantinProductViewSet, transfer_stok_kantin, tambah_stok_gudang

router = DefaultRouter()
router.register(r'gudang/produk', GudangProductViewSet)
router.register(r'kantin/produk', KantinProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('kantin/stok/transfer/', transfer_stok_kantin, name='transfer_stok_kantin'),
    path('gudang/stok/masuk/', tambah_stok_gudang, name='tambah_stok_gudang'),
]