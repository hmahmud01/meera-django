from os import stat_result
from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import OneToOneField

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=128, null=True, blank=True)
    thumb_image = models.FileField('product_thumbnail', upload_to='thumbs', blank=True, null=True)

    def __str__(self):
        return self.title

class Zone(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self) :
        return self.name

class PackSize(models.Model):
    size = models.CharField(max_length=128, null=True, blank=True)
    qty = models.FloatField(null=True, blank=True)
    measure = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self) :
        return self.size

class Product(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product_category")
    pack_size = models.ForeignKey(PackSize, on_delete=models.CASCADE, related_name="product_pack_size", blank=True, null=True)
    price = models.FloatField(null=True, blank=True)
    disc_price = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    inv_stock = models.IntegerField(null=True, blank=True)    
    status = models.BooleanField(default=True, null=True, blank=True)    
    thumb_image = models.FileField('product_thumbnail', upload_to='thumbs', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Favourite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isFavourite = models.BooleanField(default=False)
    def __str__(self):
        return f"productID = {self.product.id} | user = {self.user.username} | ISFavourite = {self.isFavourite}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.FloatField(null=True, blank=True)
    isComplete = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"User={self.user.username}|ISComplete={self.isComplete}"

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)
    price = models.FloatField()
    quantity = models.PositiveBigIntegerField()
    subtotal = models.FloatField()
    def __str__(self):
        # return f"Cart={self.cart.id}"
        return f"Cart=={self.cart.id}<==>CartProduct:{self.id}==Qualtity=={self.quantity}"


# NEW ORDER CLASS FOR APP
class OrderApp(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    email = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=13)
    address = models.CharField(max_length=200)


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

class Order(models.Model):
    customer = models.CharField(max_length=128, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    trx_id = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitems_set.all()
        
        return shipping
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitems_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitems_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

