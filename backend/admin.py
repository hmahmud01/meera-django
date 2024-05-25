from django.contrib import admin
from .models import Category, Zone, PackSize, Product, Favourite, Cart, CartProduct, OrderApp, ProductZone, ProductImage, Order, OrderItems, OrderWeb

admin.site.register([Category, Zone, PackSize, Product, Favourite, Cart, CartProduct, OrderApp, ProductZone, ProductImage, Order, OrderItems, OrderWeb])

