from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import GudangProduct, KantinProduct
from .serializers import GudangProductSerializer, KantinProductSerializer, TransferStokSerializer, TambahStokGudangSerializer, TransferResponseSerializer, TambahStokGudangResponseSerializer


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrKasir(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'kasir']


class GudangProductViewSet(viewsets.ModelViewSet):
    queryset = GudangProduct.objects.all()
    serializer_class = GudangProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdmin]


class KantinProductViewSet(viewsets.ModelViewSet):
    queryset = KantinProduct.objects.all()
    serializer_class = KantinProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminOrKasir]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


@api_view(['POST'])
@permission_classes([IsAdmin])
def transfer_stok_kantin(request):
    serializer = TransferStokSerializer(data=request.data)
    if serializer.is_valid():
        product_gudang_id = serializer.validated_data['product_gudang_id']
        quantity = serializer.validated_data['quantity']

        gudang_product = get_object_or_404(GudangProduct, id=product_gudang_id)

        if gudang_product.stock_gudang < quantity:
            return Response({'error': 'Stok gudang tidak cukup'}, status=status.HTTP_400_BAD_REQUEST)

        gudang_product.stock_gudang -= quantity
        gudang_product.save()

        kantin_product, created = KantinProduct.objects.get_or_create(
            product_gudang=gudang_product,
            defaults={'stock_kantin': 0}
        )
        kantin_product.stock_kantin += quantity
        kantin_product.save()

        response_data = {
            'message': 'Stok berhasil ditransfer ke kantin',
            'product': {
                'id': gudang_product.id,
                'name': gudang_product.name,
                'stock_gudang': gudang_product.stock_gudang,
                'stock_kantin': kantin_product.stock_kantin
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdmin])
def tambah_stok_gudang(request):
    serializer = TambahStokGudangSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = get_object_or_404(GudangProduct, id=product_id)
        product.stock_gudang += quantity
        product.save()

        response_data = {
            'message': 'Stok gudang ditambahkan',
            'product': {
                'id': product.id,
                'name': product.name,
                'stock_gudang': product.stock_gudang
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
