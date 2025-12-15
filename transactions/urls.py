from django.urls import path
from .views import payment, history

urlpatterns = [
    path('payment/', payment),
    path('history/', history),
]
