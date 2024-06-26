from django.db.models.fields import CommaSeparatedIntegerField, PositiveBigIntegerField, json
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import itertools

import json

from backend.models import Category, Order, OrderItems, PackSize, Product, ProductImage, ProductZone, Zone, OrderApp, Cart, CartProduct, Orderstatus, OrderWeb, ProductBrand, ProductPackPrice
from backend.utils import cartData

from sslcommerz_lib import SSLCOMMERZ 

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
    brands = ProductBrand.objects.all()
    return render(request, "products/create.html", {"categories": categories, "zones": zones, "packs": packs, "brands": brands})


def saveCategory(request):
    data = request.POST
    file_data = request.FILES
    category = Category(
        title = data['title'],
        thumb_image=file_data['thumb_image'],
    )
    category.save()
    return redirect('productcreate')

def saveBrand(request):
    data = request.POST
    file_data = request.FILES
    brand = ProductBrand(
        name = data['name'],
        image=file_data['image']
    )

    brand.save()
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
    print("PRINTING POST DATA")
    print(post_data)
    # <QueryDict: {'csrfmiddlewaretoken': ['EY0yam9HhBhX0LNGHRrawofSW78hMQIcDeg2H1OsTgN15h50gQurDq4XZuRU7bVF'], 
    # 'name': ['asfe'], 'category': ['3'], 'packsize': ['2'], 'packs': ['1', '2'], 
    # 'packprice': ['100', '2323'], 'brand': ['1'], 'price': ['10'], 'distributor_slab': ['10'], 
    # 'disc_price': ['2'], 'description': [''], 'inv_stock': ['10']}>
    print("PRINTING FILE DATA")
    print(file_data)
    category = Category.objects.get(id=post_data['category'])
    size = PackSize.objects.get(id=post_data['packsize'])
    brand = ProductBrand.objects.get(id=post_data['brand'])

    packs = post_data.getlist('packs')
    packprice = post_data.getlist('packprice')

    
    product = Product(
        name=post_data['name'],
        category=category,
        pack_size=size,
        brand= brand,
        price=post_data['price'],
        distributor_slab=post_data['distributor_slab'],
        disc_price=post_data['disc_price'],
        description=post_data['description'],
        inv_stock=post_data['inv_stock'],
        thumb_image=file_data['thumb_image'],
    )
    
    product.save()

    for pack, price in itertools.zip_longest(packs, packprice):
        if pack is not None:
            packsize = PackSize.objects.get(id=pack)
            productpackprice = ProductPackPrice(
                product = product,
                packsize = packsize,
                price = price
            )
            productpackprice.save()

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

def productUpdate(request, pid):
    categories = Category.objects.all()
    zones = Zone.objects.all()
    packs = PackSize.objects.all()
    product = Product.objects.get(id=pid)
    images = ProductImage.objects.filter(product_id=pid)
    return render(request, "products/create.html", {"categories": categories, "zones": zones, "packs": packs, "product": product, "images": images})

def productList(request):
    products = Product.objects.all()
    return render(request, "products/list.html", {"products": products})

def productDetail(request, pid):
    product = Product.objects.get(id=pid)
    zones = ProductZone.objects.filter(product_id=pid)
    images = ProductImage.objects.filter(product_id=pid)
    return render(request, "products/detail.html", {"product": product, "zones": zones, "images": images})

def homeproductDetail(request, pid):
    product = Product.objects.get(id=pid)
    zones = ProductZone.objects.filter(product_id=pid)
    images = ProductImage.objects.filter(product_id=pid)
    packs = ProductPackPrice.objects.filter(product_id=pid)
    return render(request, "home/homeproductdetail.html", {"product": product, "zones": zones, "images": images, "packs": packs})

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
    orderweb = OrderWeb.objects.all()
    return render(request, "orders/index.html", {"orders": orders, "weborders": orderweb})

def orderDetail(request, oid):
    order = Order.objects.get(id=oid)
    items = OrderItems.objects.filter(order_id=oid)
    
    # order = OrderApp.objects.get(id=oid)
    
    # items = CartProduct.objects.filter(cart__id=order.cart.id)
    # TODO
    # make the product item working 
    print(order)
    print(items)
    products = []
    total = 0
    for item in items:
        print(item)
        print(item.product)
        total += item.get_total
        data = {
            "product": item.product.name,
            "qty": item.quantity,
            "subtotal": item.get_total
        }
        products.append(data)

    print(products)

    return render(request, "orders/detail.html", {"order": order, "items": products, "total": total})

def updateStatus(request, oid):
    post_data = request.POST
    
    order = OrderApp.objects.get(id=oid)
    status = order.orderstatus
    status.status = post_data['status']
    status.remark = post_data['remark']
    status.save()

    return redirect('orderdetail', oid)

def userIndex(request):
    users = User.objects.all().exclude(is_superuser=True)
    return render(request, "users/index.html", {"users": users})

def userProfile(request):
    return render(request, "users/profile.html")

def inventory(request):
    products = Product.objects.all()
    return render(request, "inventory/index.html", {"products": products})

def simulator(request):
    products = Product.objects.all()
    return render(request, "simulator.html", {"products": products})

def apphome(request):
    products = Product.objects.all()
    return render(request, "web/index.html", {"products": products})

def retailer(request):
    return render(request, "home/homeretailer.html")

def brands(request):
    brands = ProductBrand.objects.all()
    return render(request, "home/homebrands.html", {"brands": brands})

def brandProducts(request, bid):
    products = Product.objects.filter(brand_id=bid)
    return render(request, "home/home.html", {"products": products})

def appcart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'home/homecart.html', context)

def appcheckout(request):
    post_data = request.POST
    order_id = post_data['order']
    order = Order.objects.get(id=order_id)
    # order.complete = True
    # order.trx_id = "meera-"+str(order.id)

    print(f"order stat: {order.complete} {order.trx_id}")
    print(order)
    print(order.get_cart_total)

    # print(order_comp)
    order.save()
    context = {'total': order.get_cart_total, 'order_id': order_id}
    return render(request, 'home/homecheckout.html', context)

def makepayment(request):
    post_data = request.POST
    print(post_data)

    print("===========printing SSL RESPONSE ===================")
    settings = { 'store_id': 'maise6244d4efe620f', 'store_pass': 'maise6244d4efe620f@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = 100.26
    post_body['currency'] = "BDT"
    post_body['tran_id'] = "12345"
    post_body['success_url'] = "your success url"
    post_body['fail_url'] = "your fail url"
    post_body['cancel_url'] = "your cancel url"
    post_body['emi_option'] = 0
    post_body['cus_name'] = "test"
    post_body['cus_email'] = "test@test.com"
    post_body['cus_phone'] = "01700000000"
    post_body['cus_add1'] = "customer address"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body)
    print(response)
    status = response['status']
    if status == "SUCCESS":
    # <QueryDict: {'csrfmiddlewaretoken': ['Z9lL7jP7kSUTfxVm6cV1YsxpXG9UiCJr5p0RbrjMN7fC1DRd80t2tImxWCGcaOmn'],
    #              'bkash': ['07975686099'], 'pin': ['1234564'], 'order': [''], 'name': ['Hasan Mahmud'], 
    #              'address': ['shantinagar, dahat'], 'phone': ['01797568609'], 'email': ['hmahmud01@gmail.com']}>
        order = Order.objects.get(id=post_data['order'])
        order.complete = True
        order.trx_id = "meera-"+str(order.id)
        # order.save()

        print(f"order stat: {order.complete} {order.trx_id}")
        print(order)
        # print(order_comp)
        order.save()
        orderweb = OrderWeb(
            order = order,
            email = post_data['email'],
            phone = post_data['phone'],
            address = post_data['address'],
            name = post_data['name']
        )
        orderweb.save()
        return redirect('successpage')
    else:

        msg = response['failedreason']
        return redirect('failedpage')

def successpage(request):
    return render(request, 'home/homesuccess.html')

def failedpage(request):
    return render(request, 'home/homefailed.html')

def payment(request):
    settings = { 'store_id': 'maise6244d4efe620f', 'store_pass': 'maise6244d4efe620f@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = 100.26
    post_body['currency'] = "BDT"
    post_body['tran_id'] = "12345"
    post_body['success_url'] = "your success url"
    post_body['fail_url'] = "your fail url"
    post_body['cancel_url'] = "your cancel url"
    post_body['emi_option'] = 0
    post_body['cus_name'] = "test"
    post_body['cus_email'] = "test@test.com"
    post_body['cus_phone'] = "01700000000"
    post_body['cus_add1'] = "customer address"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body) # API response
    print(response)
    # Need to redirect user to response['GatewayPageURL']


# CART FUNCTIONS
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print(data)

    # customer = "Some Customer"
    customer = request.user.username
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
    # <QueryDict: {'csrfmiddlewaretoken': ['qxaCFgXfhz7kpoMgEECXqCQ3gNCNiWfXpNq6cVC0TeDouU4AdDFexEF8jalqDhsq'], 'order': ['40']}>
    post_data = request.POST
    order_id = post_data['order']
    order = Order.objects.get(id=order_id)
    order.complete = True
    order.trx_id = "meera-"+str(order.id)
    # order.save()

    print(f"order stat: {order.complete} {order.trx_id}")
    print(order)
    # print(order_comp)
    order.save()
    return redirect('cart')