from django.urls import path
from .views import laporan_harian

from django.urls import path
from .views import (
    laporan_harian,
    laporan_bulanan,
    laporan_tahunan
)

urlpatterns = [
    path('laporan/harian/', laporan_harian),
    path('laporan/bulanan/', laporan_bulanan),
    path('laporan/tahunan/', laporan_tahunan),
]
