from django.db.models.fields import CommaSeparatedIntegerField, PositiveBigIntegerField, json
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

import json

from backend.models import Category, Order, OrderItems, PackSize, Product, ProductImage, ProductZone, Zone
from backend.utils import cartData

# Create your views here.

@login_required(login_url="/login/")
def home(request):
    return render(request, "index.html")

def blankpage(request):
    return render(request, "sample.html")

def login(request):
    return render(request, "login.html")

def verifyLogin(request):
    post_data = request.POST

    if 'username' and 'pass':
        user = authenticate(
            request,
            username = post_data['username'],
            password = post_data['pass']
        )

        if user is None:
            return redirect('login')
        elif user.is_superuser:
            auth_login(request, user)
            return redirect('/')
        else:
            return redirect('login')

    else:
        return redirect('login')

def userLogout(request):
    logout(request)
    return redirect('login')

def productCreate(request):
    categories = Category.objects.all()
    zones = Zone.objects.all()
    packs = PackSize.objects.all()
    return render(request, "products/create.html", {"categories": categories, "zones": zones, "packs": packs})


def saveCategory(request):
    data = request.POST
    file_data = request.FILES
    category = Category(
        title = data['title'],
        thumb_image=file_data['thumb_image'],
    )
    category.save()
    return redirect('productcreate')

def savePackSize(request):
    data = request.POST
    pack = PackSize(
        size = data['size'],
        qty = data['qty'],
        measure = data['measure']
    )
    pack.save()
    return redirect('productcreate')

def saveZone(request):
    data = request.POST
    zone = Zone(
        name = data['name']
    )
    zone.save()
    return redirect('productcreate')

# <QueryDict: {'csrfmiddlewaretoken': ['NgDZXkPCNkardxwGMHDS9OsLgfGGSsikZvTh0MJwwjqZOMDcqfdCZFgkRv2otH9V'], 
# 'name': ['Test Name'], 'category': ['op1'], 'price': ['481'], 'disc_price': ['521'], 'inv_stock': ['659'], 'zone': ['z2', 'z3']}>

# <MultiValueDict: {'thumb_image': [<InMemoryUploadedFile: LOGO.png (image/png)>], 
# 'photos': [<InMemoryUploadedFile: footer.jpg (image/jpeg)>, <InMemoryUploadedFile: footer_2.jpg (image/jpeg)>]}>

def saveProduct(request):
    post_data = request.POST
    file_data = request.FILES
    category = Category.objects.get(id=post_data['category'])
    size = PackSize.objects.get(id=post_data['packsize'])
    
    product = Product(
        name=post_data['name'],
        category=category,
        pack_size=size,
        price=post_data['price'],
        disc_price=post_data['disc_price'],
        description=post_data['description'],
        inv_stock=post_data['inv_stock'],
        thumb_image=file_data['thumb_image'],
    )
    
    product.save()

    zones = post_data.getlist("zone")
    for zone_id in zones:
        zone = Zone.objects.get(id=zone_id)
        productzone = ProductZone(
            product = product,
            zone = zone
        )
        productzone.save()

    photos = file_data.getlist('photos')
    for photo in photos:
        name = photo.name.split('/')     
        image = ProductImage(
            product = product,
            name=name,
            photo = photo
        )
        image.save()

    return redirect('productlist')    


def productList(request):
    products = Product.objects.all()
    return render(request, "products/list.html", {"products": products})

def productDetail(request, pid):
    product = Product.objects.get(id=pid)
    zones = ProductZone.objects.filter(product_id=pid)
    images = ProductImage.objects.filter(product_id=pid)
    return render(request, "products/detail.html", {"product": product, "zones": zones, "images": images})

def statusUpdate(request, state, pid):
    product = Product.objects.get(id=pid)
    if state == 'False':
        product.status = False
        product.save()
    else:
        product.status = True
        product.save()
    return redirect('productdetail', pid)

def stockupdate(request, pid):
    post_data = request.POST
    product = Product.objects.get(id=pid)
    product.inv_stock = post_data['stock']
    product.save()
    return redirect('productdetail', pid)

def orderList(request):
    orders = Order.objects.all()    
    return render(request, "orders/index.html", {"orders": orders})

def orderDetail(request, oid):
    order = Order.objects.get(id=oid)
    items = OrderItems.objects.filter(order_id=oid)
    return render(request, "orders/detail.html", {"order": order, "items": items})

def userIndex(request):
    return render(request, "users/index.html")

def userProfile(request):
    return render(request, "users/profile.html")

def inventory(request):
    products = Product.objects.all()
    return render(request, "inventory/index.html", {"products": products})

def simulator(request):
    products = Product.objects.all()
    return render(request, "simulator.html", {"products": products})


# CART FUNCTIONS
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = "Some Customer"
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItems.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was Added', safe=False)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'cart.html', context)


def processOrder(request):
    post_data = request.POST
    print(post_data['order'])
    order_id = post_data['order']
    order = Order.objects.get(id=order_id)
    order.complete = True
    order.trx_id = "meera-"+str(order.id)
    order.save()

    return redirect('cart')