from django.urls import path
from .views import tambah_pengeluaran, list_pengeluaran

urlpatterns = [
    path('pengeluaran/', tambah_pengeluaran, name='tambah_pengeluaran'),
    path('pengeluaran/list/', list_pengeluaran, name='list_pengeluaran'),
]