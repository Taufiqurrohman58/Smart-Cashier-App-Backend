from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, TransactionViewSet

router = DefaultRouter()

# Cart endpoints
router.register(r'cart', CartViewSet, basename='cart')

# Transaction endpoints
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
]