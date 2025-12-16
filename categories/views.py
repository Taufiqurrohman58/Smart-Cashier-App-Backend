from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework.permissions import BasePermission
from .models import Category
from .serializers import CategorySerializer

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrKasir(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'kasir']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminOrKasir]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

