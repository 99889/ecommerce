import django_filters
from django.db import models
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """
    Advanced filtering for products based on:
    - Category
    - Price range (min/max)
    - Stock availability
    - Name and description search
    """
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category',
        to_field_name='id'
    )
    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    
    # Price range filters
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )
    
    # Stock availability filter
    in_stock = django_filters.BooleanFilter(
        method='filter_stock_availability'
    )
    
    # Stock range filters
    min_stock = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='gte'
    )
    max_stock = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='lte'
    )

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'description': ['icontains'],
            'sku': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }

    def filter_stock_availability(self, queryset, name, value):
        """Filter products based on stock availability"""
        if value is True:
            return queryset.filter(stock__gt=0)
        elif value is False:
            return queryset.filter(stock=0)
        return queryset
