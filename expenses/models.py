from django.db import models
from django.conf import settings


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    deskripsi = models.CharField(max_length=255)
    jumlah = models.DecimalField(max_digits=10, decimal_places=2)
    tanggal = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.deskripsi} - {self.jumlah}"
