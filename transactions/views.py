from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.db import transaction as db_transaction
from .models import Transaction, TransactionItem
from produks.models import KantinProduct


class IsKasir(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'kasir'

@api_view(['POST'])
@permission_classes([IsKasir])
def payment(request):
    items = request.data.get('items')
    uang_bayar = request.data.get('uang_bayar')

    if not items or not uang_bayar:
        return Response({'error': 'Items and payment amount are required.'}, status=status.HTTP_400_BAD_REQUEST)

    subtotal = 0
    validated_items = []

    # Validate each item and calculate subtotal
    for item in items:
        product_id = item.get('product_id')
        qty = item.get('qty')

        if not product_id or not qty:
            return Response({'error': 'Invalid item data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = KantinProduct.objects.get(id=product_id)
        except KantinProduct.DoesNotExist:
            return Response({'error': f'Product with id {product_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        if product.stock_kantin < qty:
            return Response({'error': f'Insufficient stock for {product.name}.'}, status=status.HTTP_400_BAD_REQUEST)

        total = product.price * qty
        subtotal += total

        validated_items.append({'product': product, 'qty': qty, 'total': total})

    if uang_bayar < subtotal:
        return Response({'error': 'Payment amount is less than the subtotal.'}, status=status.HTTP_400_BAD_REQUEST)

    kembalian = uang_bayar - subtotal

    with db_transaction.atomic():
        transaction = Transaction.objects.create(
            user=request.user,
            total=subtotal,
            cash_given=uang_bayar,
            change=kembalian,
            payment_method='cash'
        )

        for item in validated_items:
            product = item['product']
            qty = item['qty']
            total = item['total']

            TransactionItem.objects.create(
                transaction=transaction,
                product=product,
                qty=qty,
                price=product.price,
                subtotal=total
            )

            product.stock_kantin -= qty
            product.save()

    response_data = {
        'status': True,
        'invoice': transaction.invoice,
        'subtotal': subtotal,
        'uang_bayar': uang_bayar,
        'kembalian': kembalian
    }

    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history(request):
    if request.user.role == 'admin':
        transactions = Transaction.objects.all().order_by('-created_at')
    else:
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    result = []
    for trx in transactions:
        items = [
            {
                'name': item.product.name,
                'qty': item.qty,
                'subtotal': item.subtotal
            }
            for item in trx.items.all()

        ]

        result.append({
            'invoice': trx.invoice,
            'total': trx.total,
            'uang_bayar': trx.cash_given,
            'kembalian': trx.change,
            'kasir': trx.user.username,
            'created_at': trx.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items
        })

    return Response(result, status=status.HTTP_200_OK)
