from os import stat_result
from django.db import models
from django.db.models.base import Model

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.title
    

class Zone(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self) :
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product_category")
    price = models.FloatField(null=True, blank=True)
    disc_price = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    inv_stock = models.IntegerField(null=True, blank=True)    
    status = models.BooleanField(default=True, null=True, blank=True)    
    thumb_image = models.FileField('product_thumbnail', upload_to='thumbs', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return self.name

class ProductZone(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="product_zone")

    def __str__(self):
        return self.zone.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    name = models.CharField(max_length=128, null=True, blank=True)
    photo = models.FileField('product_photo', upload_to='photos', blank=True, null=True)

    def __str__(self):
        return self.product.name
