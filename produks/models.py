from django.db import models

class GudangProduct(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_gudang = models.PositiveIntegerField(default=0)
    satuan = models.CharField(max_length=50, default='pcs')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class KantinProduct(models.Model):
    product_gudang = models.ForeignKey(GudangProduct, on_delete=models.CASCADE, related_name='kantin_products')
    stock_kantin = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_gudang.name} - Kantin"

    @property
    def name(self):
        return self.product_gudang.name

    @property
    def price(self):
        return self.product_gudang.price

    @property
    def image(self):
        return self.product_gudang.image

    @property
    def satuan(self):
        return self.product_gudang.satuan
