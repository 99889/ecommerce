from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Cart, CartItem
from products.models import Product
from .serializers import (
    OrderSerializer, OrderCreateSerializer, CartSerializer,
    CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    OrderStatusUpdateSerializer
)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related(
            'order_items__product__category'
        )

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related(
            'order_items__product__category'
        )

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not cart.cart_items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate total price and check stock
        total_price = 0
        order_items_data = []
        
        for cart_item in cart.cart_items.all():
            if cart_item.product.stock < cart_item.quantity:
                return Response(
                    {'error': f'Insufficient stock for {cart_item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            total_price += cart_item.product.price * cart_item.quantity
            order_items_data.append({
                'product': cart_item.product,
                'quantity': cart_item.quantity,
                'price': cart_item.product.price
            })
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            shipping_address=serializer.validated_data['shipping_address']
        )
        
        # Create order items and reduce product stock
        for item_data in order_items_data:
            OrderItem.objects.create(
                order=order,
                **item_data
            )
            item_data['product'].reduce_stock(item_data['quantity'])
        
        # Clear cart
        cart.cart_items.all().delete()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock < quantity:
            return Response(
                {'error': 'Insufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return Response(
                    {'error': 'Insufficient stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.save()
        
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateCartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        serializer = self.get_serializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        new_quantity = serializer.validated_data.get('quantity', cart_item.quantity)
        
        if new_quantity > cart_item.product.stock:
            return Response(
                {'error': 'Insufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return Response(CartItemSerializer(cart_item).data)


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Admin-only view to update order status"""
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAdminUser]
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # The signal in models.py will handle sending real-time notifications
        return response
