from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Cart, CartItem, Transaction, TransactionItem
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    TransactionSerializer, CheckoutSerializer
)
from produks.models import Product 


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        """Get or create cart for user"""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @action(detail=False, methods=['get'])
    def view(self, request):
        """View current cart"""
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        qty = serializer.validated_data['qty']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart = self.get_cart(request.user)

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'qty': qty}
        )

        if not created:
            cart_item.qty += qty
            cart_item.save()

        # Return cart item with additional data
        response_data = {
            'message': 'Product added to cart',
            'cart_item': {
                'id': cart_item.id,
                'product_id': cart_item.product.id,
                'product_name': cart_item.product.name,
                'price': cart_item.product.price,
                'qty': cart_item.qty,
                'subtotal': cart_item.subtotal,
                'product_image': cart_item.product.image
            },
            'cart_summary': {
                'total_items': cart.total_items,
                'total_price': cart.total_price
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'])
    def update_item(self, request, pk=None):
        """Update cart item quantity"""
        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        qty = request.data.get('qty')
        if not qty or qty < 1:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.qty = qty
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """Remove item from cart"""
        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


class TransactionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Process checkout and create transaction"""
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = serializer.validated_data['items']
        total = serializer.validated_data['total']
        cash_given = serializer.validated_data['cash_given']
        payment_method = serializer.validated_data['payment_method']
        change = serializer.validated_data['change']

        cart = get_object_or_404(Cart, user=request.user)

        # Validate cart items match request
        cart_items = {item['product_id']: item['qty'] for item in items_data}
        actual_cart_items = {item.product.id: item for item in cart.cartitem_set.all()}

        if set(cart_items.keys()) != set(actual_cart_items.keys()):
            return Response({'error': 'Cart items do not match request'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate and verify total
        calculated_total = sum(
            actual_cart_items[product_id].subtotal
            for product_id in cart_items.keys()
        )

        if abs(calculated_total - total) > 0.01:  # Allow small floating point differences
            return Response({'error': 'Total amount mismatch'}, status=status.HTTP_400_BAD_REQUEST)

        # Create transaction atomically
        with db_transaction.atomic():
            # Create transaction
            transaction = Transaction.objects.create(
                user=request.user,
                total=total,
                cash_given=cash_given,
                change=change,
                payment_method=payment_method
            )

            # Create transaction items
            for product_id, qty in cart_items.items():
                cart_item = actual_cart_items[product_id]
                TransactionItem.objects.create(
                    transaction=transaction,
                    product=cart_item.product,
                    qty=qty,
                    price=cart_item.product.price,
                    subtotal=cart_item.subtotal
                )

            # Clear cart
            cart.cartitem_set.all().delete()

        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get transaction history"""
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        """Get transaction detail"""
        try:
            transaction = Transaction.objects.get(id=pk, user=request.user)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """Get text-based receipt for transaction"""
        try:
            transaction = Transaction.objects.get(id=pk, user=request.user)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create text receipt
        receipt_lines = []
        receipt_lines.append("=" * 40)
        receipt_lines.append("         STRUK PEMBELIAN")
        receipt_lines.append("=" * 40)
        receipt_lines.append(f"No. Transaksi: #{transaction.id}")
        receipt_lines.append(f"Tanggal: {transaction.created_at.strftime('%d/%m/%Y %H:%M')}")
        receipt_lines.append(f"Kasir: {transaction.user.username}")
        receipt_lines.append(f"Metode: {transaction.payment_method.upper()}")
        receipt_lines.append("-" * 40)

        # Items
        receipt_lines.append("Detail Pembelian:")
        receipt_lines.append("-" * 40)
        for item in transaction.transactionitem_set.all():
            receipt_lines.append(f"{item.product.name}")
            receipt_lines.append(f"  {item.qty} x Rp {item.price:,.0f} = Rp {item.subtotal:,.0f}")
        receipt_lines.append("-" * 40)

        # Totals
        receipt_lines.append(f"Total: Rp {transaction.total:,.0f}")
        if transaction.cash_given:
            receipt_lines.append(f"Bayar: Rp {transaction.cash_given:,.0f}")
            receipt_lines.append(f"Kembalian: Rp {transaction.change:,.0f}")

        receipt_lines.append("=" * 40)
        receipt_lines.append("Terima kasih atas pembelian Anda!")
        receipt_lines.append("=" * 40)

        receipt_text = "\n".join(receipt_lines)

        return Response({
            'receipt_text': receipt_text,
            'transaction_id': transaction.id
        })

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        """Get AI recommendations for products"""
        # Simple rule-based recommender
        # Get products ordered by total sales in the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        top_products = TransactionItem.objects.filter(
            transaction__created_at__gte=thirty_days_ago
        ).values('product').annotate(
            total_sold=Sum('qty')
        ).order_by('-total_sold')[:5]

        product_ids = [item['product'] for item in top_products]
        recommended_products = Product.objects.filter(
            id__in=product_ids,
            is_active=True
        ).order_by('-id')  # Simple ordering

        # Also get products by category if we have sales data
        category_sales = TransactionItem.objects.filter(
            transaction__created_at__gte=thirty_days_ago
        ).values('product__category').annotate(
            total_sold=Sum('qty')
        ).order_by('-total_sold')[:1]

        if category_sales:
            top_category = category_sales[0]['product__category']
            category_products = Product.objects.filter(
                category=top_category,
                is_active=True
            ).exclude(id__in=product_ids)[:3]

            recommendations = list(recommended_products) + list(category_products)
        else:
            recommendations = list(recommended_products)

        # Format response
        result = []
        for product in recommendations[:5]:  # Limit to 5 recommendations
            result.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': product.price,
                'image': product.image
            })

        return Response({
            'recommendations': result,
            'algorithm': 'rule_based',
            'description': 'Products recommended based on sales popularity and category trends'
        })
