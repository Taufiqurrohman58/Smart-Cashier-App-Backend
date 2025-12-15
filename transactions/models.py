from django.db import models
from django.conf import settings
from produks.models import KantinProduct
from django.utils import timezone


class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('digital', 'Digital Wallet'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    invoice = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cash_given = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice:
            year = timezone.now().year
            last = Transaction.objects.filter(
                created_at__year=year
            ).order_by('-id').first()

            last_number = (
                int(last.invoice.split('-')[-1])
                if last and last.invoice
                else 0
            )

            self.invoice = f"INV-{year}-{last_number + 1:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice

class TransactionItem(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        KantinProduct,
        on_delete=models.CASCADE
    )

    qty = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} x {self.qty}"
