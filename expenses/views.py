from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Expense
from .serializers import ExpenseSerializer, ExpenseCreateSerializer


class IsKasir(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'kasir'


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


@api_view(['POST'])
@permission_classes([IsKasir])
def tambah_pengeluaran(request):
    serializer = ExpenseCreateSerializer(data=request.data)
    if serializer.is_valid():
        expense = serializer.save(user=request.user)
        response_serializer = ExpenseSerializer(expense)
        return Response({
            'status': True,
            'message': 'Pengeluaran berhasil ditambahkan',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdmin])
def list_pengeluaran(request):
    date_filter = request.query_params.get('date')
    if date_filter:
        expenses = Expense.objects.filter(tanggal=date_filter).order_by('-created_at')
    else:
        expenses = Expense.objects.all().order_by('-created_at')

    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
