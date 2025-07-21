from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Create initial data for products and categories'

    def handle(self, *args, **options):
        User = get_user_model()

        # Create admin user
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='password123'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created with email admin@example.com and password password123'))

        # Create categories
        categories = ['Books', 'Electronics', 'Fashion', 'Furniture']
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Category [32m{category_name}[0m created'))

        # Create sample products
        for _ in range(20):
            category = Category.objects.order_by('?').first()  # Random category
            product_name = get_random_string(length=8)
            Product.objects.create(
                name=product_name,
                description=f'{product_name} description',
                price=10.0,
                stock=100,
                category=category,
                sku=get_random_string(length=12).upper()
            )
            self.stdout.write(self.style.SUCCESS(f'Product [32m{product_name}[0m created in [33m{category.name}[0m category'))

        self.stdout.write(self.style.SUCCESS('Initial data creation complete.'))
