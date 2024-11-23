import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meera.settings')
django.setup()

from backend.models import Product
from django.utils.text import slugify

products = Product.objects.all()
for product in products:
    if not product.slug:
        product.slug = slugify(product.name)
        product.save()
        print(f"Updated slug for Product ID {product.id}")