from django.core.management.base import BaseCommand
from django.utils.text import slugify
from backend.models import Product

class Command(BaseCommand):
    help = "Populate slugs for existing products"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            if not product.slug:
                product.slug = slugify(product.name)
                product.save()
                self.stdout.write(self.style.SUCCESS(f"Updated slug for Product ID {product.id}"))
        self.stdout.write(self.style.SUCCESS("Slugs populated successfully!"))