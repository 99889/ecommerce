from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

User = get_user_model()

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"
    
    def get_total_quantity(self):
        return sum(item.quantity for item in self.order_items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.price * self.quantity

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s cart"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.cart_items.all())
    
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity

# Signal to send real-time notifications when order status changes
@receiver(post_save, sender=Order)
def send_order_status_notification(sender, instance, created, **kwargs):
    """Send real-time notification when order status changes"""
    if not created and 'status' in getattr(instance, '_dirty_fields', []):
        # Create database notification
        from notifications.models import Notification
        Notification.objects.create(
            user=instance.user,
            title='Order Status Update',
            message=f'Your order #{instance.id} status has been updated to {instance.get_status_display()}',
            notification_type='order_status_update',
            data={
                'order_id': instance.id,
                'status': instance.status,
                'order_total': str(instance.total_price)
            }
        )
        
        # Send real-time notification via WebSocket
        channel_layer = get_channel_layer()
        notification_data = {
            'type': 'order_status_update',
            'order_id': instance.id,
            'status': instance.status,
            'status_display': instance.get_status_display(),
            'message': f'Your order #{instance.id} status has been updated to {instance.get_status_display()}'
        }
        
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.user.id}',
            {
                'type': 'send_notification',
                'message': json.dumps(notification_data)
            }
        )
    elif created:
        # Create notification for new order
        from notifications.models import Notification
        Notification.objects.create(
            user=instance.user,
            title='Order Created',
            message=f'Your order #{instance.id} has been created successfully!',
            notification_type='order_created',
            data={
                'order_id': instance.id,
                'order_total': str(instance.total_price)
            }
        )
