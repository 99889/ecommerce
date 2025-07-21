from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['stock']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        """Reduce product stock when ordered"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

# Cache invalidation signals
@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, **kwargs):
    """Invalidate product cache when product is saved or deleted"""
    cache.delete_many([
        'products_list',
        'categories_list',
        f'product_{kwargs.get("instance").id if kwargs.get("instance") else "all"}'
    ])

@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, **kwargs):
    """Invalidate category cache when category is saved or deleted"""
    cache.delete('categories_list')
