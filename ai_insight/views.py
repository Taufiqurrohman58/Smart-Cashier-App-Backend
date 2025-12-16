from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum
from datetime import timedelta, date

from transactions.models import TransactionItem
from produks.models import KantinProduct
from .permissions import IsAdmin

@api_view(['GET'])
@permission_classes([IsAdmin])
def insight_penjualan(request):
    data = (
        TransactionItem.objects
        .values('product__product_gudang__name')
        .annotate(
            total_qty=Sum('qty'),
            total_pendapatan=Sum('subtotal')
        )
        .order_by('-total_qty')
    )

    result = []
    for d in data:
        result.append({
            'produk': d['product__product_gudang__name'],
            'total_terjual': d['total_qty'],
            'total_pendapatan': d['total_pendapatan']
        })

    return Response({
        'status': True,
        'insight': result
    })

@api_view(['GET'])
@permission_classes([IsAdmin])
def rekomendasi_stok(request):
    rekomendasi = []

    for kp in KantinProduct.objects.select_related('product_gudang'):
        total_terjual = (
            TransactionItem.objects
            .filter(product=kp)
            .aggregate(total=Sum('qty'))['total'] or 0
        )

        if total_terjual > 50:
            saran = kp.stock_kantin + 20
            alasan = 'Penjualan tinggi'
        else:
            saran = kp.stock_kantin
            alasan = 'Penjualan stabil'

        rekomendasi.append({
            'produk': kp.product_gudang.name,
            'stok_sekarang': kp.stock_kantin,
            'saran_stok': saran,
            'alasan': alasan
        })

    return Response({
        'status': True,
        'rekomendasi': rekomendasi
    })

@api_view(['GET'])
@permission_classes([IsAdmin])
def prediksi_barang_habis(request):
    hasil = []
    today = date.today()
    last_7_days = today - timedelta(days=7)

    for kp in KantinProduct.objects.select_related('product_gudang'):
        total_7_hari = (
            TransactionItem.objects.filter(
                product=kp,
                transaction__created_at__date__gte=last_7_days
            ).aggregate(total=Sum('qty'))['total'] or 0
        )

        rata_per_hari = total_7_hari / 7 if total_7_hari > 0 else 0

        if rata_per_hari > 0:
            estimasi_habis = int(kp.stock_kantin / rata_per_hari)
            status = 'Segera Habis' if estimasi_habis <= 3 else 'Aman'
        else:
            estimasi_habis = 999
            status = 'Tidak Ada Penjualan'

        hasil.append({
            'produk': kp.product_gudang.name,
            'stok_sekarang': kp.stock_kantin,
            'estimasi_habis_hari': estimasi_habis,
            'status': status
        })

    return Response({
        'status': True,
        'prediksi': hasil
    })
