from django.urls import path
from .views import (
    OrderListView, OrderDetailView, OrderCreateView,
    CartView, AddToCartView, CartItemDetailView, OrderStatusUpdateView
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/update-status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/items/<int:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),
]
