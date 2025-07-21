from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.cache import cache
from django.db.models import Q
from .models import Product, Category
from .serializers import (
    ProductSerializer, ProductDetailSerializer, CategorySerializer,
    ProductCreateUpdateSerializer
)
from .filters import ProductFilter


class ProductPagination(PageNumberPagination):
    """Custom pagination for products - limit 10 per page as required"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Try to get from cache first
        categories = cache.get('categories_list')
        if categories is None:
            categories = Category.objects.all().order_by('name')
            cache.set('categories_list', categories, timeout=3600)  # 1 hour cache
        return categories

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name', 'stock']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Try to get from cache first
        cache_key = 'products_list'
        products = cache.get(cache_key)
        if products is None:
            products = Product.objects.select_related('category').all()
            cache.set(cache_key, products, timeout=3600)  # 1 hour cache
        return products
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category')
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_object(self):
        product_id = self.kwargs.get('pk')
        cache_key = f'product_{product_id}'
        product = cache.get(cache_key)
        if product is None:
            product = super().get_object()
            cache.set(cache_key, product, timeout=3600)  # 1 hour cache
        return product
