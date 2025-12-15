from django.urls import path
from .views import CreateAdminView, CreateKasirView, LoginView, LogoutView

urlpatterns = [
    path('create-admin/', CreateAdminView.as_view(), name='create_admin'),
    path('create-kasir/', CreateKasirView.as_view(), name='create_kasir'),
    path('admin/', LoginView.as_view(), name='admin_login'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]