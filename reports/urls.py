from django.urls import path
from .views import (
    laporan_harian,
    laporan_bulanan,
    laporan_tahunan,
    export_rekap_kantin_excel
)

urlpatterns = [
    path('laporan/harian/', laporan_harian),
    path('laporan/bulanan/', laporan_bulanan),
    path('laporan/tahunan/', laporan_tahunan),

    path(
        'kantin/rekap/export-excel/',
        export_rekap_kantin_excel,
        name='export_rekap_kantin_excel'
    ),
]
