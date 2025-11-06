# from django.db.models.fields import CommaSeparatedIntegerField, PositiveBigIntegerField, json
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from urllib.parse import urlencode
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
import itertools
import urllib.parse
import json
import smtplib

from backend.models import Category, Order, OrderItems, PackSize, Product, ProductImage, ProductZone, Zone, OrderApp, Cart, CartProduct, Orderstatus, OrderWeb, ProductBrand, ProductPackPrice, SubCategory, Profile, ProductText, ShippingCharge
from backend.utils import cartData

from sslcommerz_lib import SSLCOMMERZ 

# Create your views here.

@login_required(login_url="/login/")
def home(request):
    data = cartData(request)
    order = data['order']
    context = {'order':order}
    return render(request, "index.html", context)

def blankpage(request):
    return render(request, "sample.html")

def login(request):
    return render(request, "login.html")

def verifyLogin(request):
    post_data = request.POST
    print(post_data)
    print(request.user)
    if 'username' and 'pass' in post_data:
        user = authenticate(
            request,
            username = post_data['username'],
            password = post_data['pass']
        )

        print(f"AUTHENTICATION {request.user.is_authenticated}")

        print(user)

        if user is None:
            print("NOT FOUND")
            return redirect('storelogin')
        elif user.is_superuser:
            auth_login(request, user)
            return redirect('home')
        else:
            auth_login(request, user)
            print(f"user is {user.username}")
            return redirect('/')

    else:
        return redirect('storelogin')

def userLogout(request):
    logout(request)
    return redirect('store')

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

def homeproductDetail(request, slug):
    data = cartData(request)
    order = data['order']
    product = Product.objects.get(slug=slug)
    zones = ProductZone.objects.filter(product_id=product.id)
    images = ProductImage.objects.filter(product_id=product.id)
    packs = ProductPackPrice.objects.filter(product_id=product.id)
    texts = ProductText.objects.filter(product_id=product.id)
    stock = product.inv_stock
    available = True
    if stock is None:
        available = False

    if stock == 0:
        available = False
    # return render(request, "home/homeproductdetail.html", {"product": product, "zones": zones, "images": images, "packs": packs})
    return render(request, "web/productdetail.html", {"product": product, "zones": zones, "images": images, "packs": packs, "texts": texts, "available": available, 'order': order})

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
    orderweb = OrderWeb.objects.get(order_id=oid)
    print(order)
    print(items)
    products = []
    total = 0
    for item in items:
        print(item)
        print(item.product)
        total += item.get_total
        data = {
            "thumb_image": item.product.thumb_image,
            "product": item.product.name,
            "price": item.product.price,
            "brand": item.product.brand,
            "category": item.product.category,
            "pack_size": item.product.pack_size,
            "qty": item.quantity,
            "subtotal": item.get_total
        }
        products.append(data)

    print(products)

    return render(request, "orders/detail.html", {"order": order, "items": products, "total": total, "web": orderweb})

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
    data = cartData(request)
    order = data['order']
    context = {'order':order}
    # return render(request, "web/index.html", {"products": products})
    return render(request, "landing/index.html")

def appstore(request):
    print(f"AUTHENTICATION USER {request.user.is_authenticated}")
    data = cartData(request)
    order = data['order']
    context = {'order':order}
    products = Product.objects.filter(status=True)
    # brands = ProductBrand.objects.filter(id=1)
    brands = ProductBrand.objects.all()
    combined_data = []

    for brand in brands:
        # Fetch subcategories related to the current brand
        subcategories = SubCategory.objects.filter(brand=brand)
        brand_data = {
            'brand_name': brand.name,
            'subcategories': []
        }

        for subcategory in subcategories:
            # Fetch categories related to the current subcategory
            categories = Category.objects.filter(subcategory=subcategory)
            subcategory_data = {
                'subcategory_title': subcategory.title,
                'categories': []
            }

            for category in categories:
                subcategory_data['categories'].append({
                    'id': category.id,
                    'category_title': category.title
                })

            brand_data['subcategories'].append(subcategory_data)

        combined_data.append(brand_data)

    # [{'brand_name': 'Rijk-Zwaan', 'subcategories': [{'subcategory_title': 'Indoor', 'categories': [{'category_title': 'Tomato'}, {'category_title': 'Cucumber'}]}, {'subcategory_title': 'Outdoor', 'categories': [{'category_title': 'Capsicum'}]}]}, {'brand_name': 'Meera', 'subcategories': []}]
    print("PRINTING COMBINED DATA")
    print(combined_data)

    return render(request, "web/index.html", {"products": products, 'datas': combined_data, 'order': order})

def meera_store(request):
    print(f"AUTHENTICATION USER {request.user.is_authenticated}")
    data = cartData(request)
    order = data['order']
    products = Product.objects.filter(brand__id=3, status=True)
    brands = ProductBrand.objects.filter(id=3)
    combined_data = []

    for brand in brands:
        # Fetch subcategories related to the current brand
        subcategories = SubCategory.objects.filter(brand=brand)
        brand_data = {
            'brand_name': brand.name,
            'subcategories': []
        }

        for subcategory in subcategories:
            # Fetch categories related to the current subcategory
            categories = Category.objects.filter(subcategory=subcategory)
            subcategory_data = {
                'subcategory_title': subcategory.title,
                'categories': []
            }

            for category in categories:
                subcategory_data['categories'].append({
                    'id': category.id,
                    'category_title': category.title
                })

            brand_data['subcategories'].append(subcategory_data)

        combined_data.append(brand_data)

    # [{'brand_name': 'Rijk-Zwaan', 'subcategories': [{'subcategory_title': 'Indoor', 'categories': [{'category_title': 'Tomato'}, {'category_title': 'Cucumber'}]}, {'subcategory_title': 'Outdoor', 'categories': [{'category_title': 'Capsicum'}]}]}, {'brand_name': 'Meera', 'subcategories': []}]
    print("PRINTING COMBINED DATA")
    print(combined_data)

    return render(request, "web/index_meera.html", {"products": products, 'datas': combined_data, 'order': order})

def categoryProduct(request, pid):
    print(pid)
    # category = Category.objects.get()
    data = cartData(request)
    order = data['order']
    products = Product.objects.filter(category__id=pid)
    brands = ProductBrand.objects.filter(id=1)
    combined_data = []

    for brand in brands:
        # Fetch subcategories related to the current brand
        subcategories = SubCategory.objects.filter(brand=brand)
        brand_data = {
            'brand_name': brand.name,
            'subcategories': []
        }

        for subcategory in subcategories:
            # Fetch categories related to the current subcategory
            categories = Category.objects.filter(subcategory=subcategory)
            subcategory_data = {
                'subcategory_title': subcategory.title,
                'categories': []
            }

            for category in categories:
                subcategory_data['categories'].append({
                    'id': category.id,
                    'category_title': category.title
                })

            brand_data['subcategories'].append(subcategory_data)

        combined_data.append(brand_data)

    # [{'brand_name': 'Rijk-Zwaan', 'subcategories': [{'subcategory_title': 'Indoor', 'categories': [{'category_title': 'Tomato'}, {'category_title': 'Cucumber'}]}, {'subcategory_title': 'Outdoor', 'categories': [{'category_title': 'Capsicum'}]}]}, {'brand_name': 'Meera', 'subcategories': []}]
    print(combined_data)
    return render(request, "web/index.html", {"products": products, 'datas': combined_data, 'order': order})

def storelogin(request):
    return render(request, "web/login.html")

def storeregister(request):
    return render(request, "web/register.html")

def userregistration(request):
    # <QueryDict: {'csrfmiddlewaretoken': ['znoabhOC6asArZly6xI2LukPUp10Ch8GDHBhD3cCEQSaG5MmTGwdMacWVC0onVFu'], 
    # 'name': ['atest'], 'phone': ['321561'], 'email': ['sadf@sdfe.com'], 
    # 'password': ['321564'], 'address': ['asdfe'], 'city': ['32asefe'], 'zip': ['321fasef']}>
    post_data = request.POST

    username = post_data['phone']

    if User.objects.filter(username=username).exists():
        msg = f"USER ALREADY EXIST WITH THIS {username}"
        return redirect('storeregister')
    else:
        print("USER DONT EXIST")
        msg = f"REGISTERED SUCCESSFULLY. PLEASE LOGIN WITH YOUR PHONE NUMBER"
        print(post_data['phone'])
        print(post_data['email'])
        print(post_data['password'])
        user = User.objects.create_user(post_data['phone'], post_data['email'], post_data['password'])
        print(user)
        profile = Profile(
            user = user,
            name = post_data['name'],
            phone = post_data['phone'],
            email = post_data['email'],
            address = post_data['address'],
            city = post_data['city'],
            zip = post_data['zip']
        )

        profile.save()
        print(profile)
        return redirect('storelogin')

def userorders(request):
    data = cartData(request)
    order = data['order']
    all_orders = []
    if request.user.is_authenticated:
        customer = request.user.username
        orders = Order.objects.filter(
            customer=customer, complete=True)
        print(orders)
        
        # items = order.orderitems_set.all()
        # cartItems = order.get_cart_items

    for order in orders:
        # items = order.order_items_set.all()
        orderweb = OrderWeb.objects.get(order_id=order.id)
        items = OrderItems.objects.filter(order_id=order.id)
        cartItems = order.get_cart_items
        cart_total = order.get_cart_total

        obj = {
            'id': order.id,
            'order': order,
            'items': items,
            'cartItems': cartItems,
            'cart_total': cart_total,
            'status': orderweb.status,
            'payment_status': orderweb.payment_status
        }

        all_orders.append(obj)
        
    all_orders.reverse()

    context = {'orders': all_orders, 'order': order }


    print(context)
    return render(request, "web/userorder.html", context)

def growersupport(request):
    return render(request, "web/basic_pages/grower_support.html")

def tutorials(request):
    return render(request, "web/basic_pages/tutorials.html")

def solutions(request):
    return render(request, "web/basic_pages/solutions.html")

def news(request):
    return render(request, "web/basic_pages/news.html")

def retailer(request):
    return render(request, "web/retailer.html")

def brands(request):
    brands = ProductBrand.objects.all()
    return render(request, "web/brands.html", {"brands": brands})

def brandProducts(request, bid):
    products = Product.objects.filter(brand_id=bid)
    return render(request, "web/index.html", {"products": products})

def appcart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    cart_total = order.get_cart_total
    charge = ShippingCharge.objects.get(type="local")
    print(charge)
    total = cart_total + charge.charge
    context = {'items':items, 'order':order, 'cartItems':cartItems, 'total': total, 'charge': charge}
    print("====context====")
    print(context)
    return render(request, 'web/cart.html', context)

def appcheckout(request):
    data = cartData(request)
    print(f"USERNAME : {request.user.username}")
    print(f"passwd : {request.user.password}")
    cartItems = data['cartItems']
    orderdata = data['order']
    items = data['items']

    print(f"order data: {data}")
    print(f"order : {orderdata}")

    post_data = request.POST
    print(f"post data : {post_data}")
    order_id = post_data['order']
    print(f"ORDER ID : {order_id}")
    order = Order.objects.get(id=order_id)

    print(f"order stat: {order.complete} {order.trx_id}")
    print(order)
    print(order.get_cart_total)

    cart_total = order.get_cart_total
    charge = ShippingCharge.objects.get(type="local")
    total = cart_total + charge.charge
    print(charge)
    total = cart_total + charge.charge

    # print(order_comp)
    order.save()
    context = {'cart_total': order.get_cart_total, 'charge': charge, 'total': total, 'order_id': order_id, 'items': items}
    return render(request, 'web/checkout.html', context)

def zoho_login(request):
    """Redirects to Zoho OAuth for authentication"""
    auth_url = f"{settings.ZOHO_AUTH_URL}?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": settings.ZOHO_CLIENT_ID,
        "redirect_uri": settings.ZOHO_REDIRECT_URI,
        "scope": "ZohoMail.messages.ALL",
        "access_type": "offline",
    })
    return redirect(auth_url)

def zoho_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)

    token_url = settings.ZOHO_TOKEN_URL
    data = {
        "client_id": settings.ZOHO_CLIENT_ID,
        "client_secret": settings.ZOHO_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": settings.ZOHO_REDIRECT_URI,
        "code": code,
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        # Store refresh_token securely (database or Django cache)
        request.session["zoho_access_token"] = tokens["access_token"]
        return JsonResponse(tokens)
    else:
        return JsonResponse(response.json(), status=400)
    
# def send_order_email(request):
#     """Sends an order confirmation email to customer & store owner"""
#     print(f"ORDER : {order.trx_id}")
#     print(f"EMAIL: {customer_email}")
#     subject = f"Order Confirmation - #{order.trx_id}"
#     charge = ShippingCharge.objects.get(type="local")
#     total = order.get_cart_total + charge.charge
#     # Load email content from a template
#     context = {
#         "order": order,
#         "customer_email": customer_email,
#         "total": total
#     }
#     message = render_to_string("emails/order_confirmation.html", context)

#     # Send email to both store owner and customer
#     recipients = ["retail.meeraseed@gmail.com", customer_email]

#     email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
#     email.content_subtype = "html"  # Ensure HTML rendering
#     email.send()

# def sendemail(request):
#     post_data = request.POST
#     order = Order.objects.get(id=post_data['order'])
#     send_order_email(order, "hmahmud01@gmail.com")
#     print(order)

def send_email_smtp(request):
    server = smtplib.SMTP_SSL("smtp.zoho.com", 465)  # No 'keyfile' argument!
    server.login("cs@meeraseed.com", "yZ9Eh4mbg1dg")
    print("server LOGGED IN")
    recipients = ["retail.meeraseed@gmail.com", "storeowner@meeraseed.com"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test Email"
    msg["From"] = "cs@meeraseed.com"
    msg["To"] = "hmahmud01@gmail.com"
    # msg["To"] = ", ".join(recipients)  # Join for display

    html_content = render_to_string("emails/order_email.html", {
        "customer_name": "Alice",
        "order_id": "ORD12345",
        "total_price": "$49.99"
    })

    # Attach plain and HTML versions
    msg.attach(MIMEText(html_content, "html"))

    # server.sendmail("cs@meeraseed.com", "hmahmud01@gmail.com", msg.as_string())
    server.send_message(msg)
    # server.sendmail(msg["From"], recipients, msg.as_string())
    server.quit()
    print("EMAIL SENT")

    return redirect("/")

def send_email_from_payment(data):
    print("INSIDE SEND EMAIL FROM PAYMENT")
    print(data["status"])
    print(data)
    trx_id = data["trx_id"]
    name = data["name"]
    server = smtplib.SMTP_SSL("smtp.zoho.com", 465)
    server.login("cs@meeraseed.com", "yZ9Eh4mbg1dg")
    print("server LOGGED IN")
    recipients = ["retail.meeraseed@gmail.com", data["email"]]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Order Confirmed for ORDER ID # {trx_id}"
    msg["From"] = "cs@meeraseed.com"
    msg["To"] = ", ".join(recipients)

    order = Order.objects.get(id=data["oid"])
    charge = ShippingCharge.objects.get(type="local")
    total = order.get_cart_total + charge.charge

    items = OrderItems.objects.filter(order_id=data["oid"])
    products = []
    for item in items:
        data = {
            "thumb_image": item.product.thumb_image,
            "product": item.product.name,
            "price": item.product.price,
            "brand": item.product.brand,
            "category": item.product.category,
            "pack_size": item.product.pack_size,
            "qty": item.quantity,
            "subtotal": item.get_total
        }
        products.append(data)

    html_content = render_to_string("emails/order_email.html", {
        "customer_name": name,
        "order_id": trx_id,
        "total_price": total,
        "charge": charge.charge,
        "products": products
    })

    # Attach plain and HTML versions
    msg.attach(MIMEText(html_content, "html"))

    # server.sendmail("cs@meeraseed.com", "hmahmud01@gmail.com", msg.as_string())
    # server.send_message(msg)
    server.sendmail(msg["From"], recipients, msg.as_string())
    server.quit()
    print("EMAIL SENT")

def send_order_email(request):
    """Sends an order confirmation email to customer & store owner"""
    print("INSIDE SEND ORDER")
    access_token = request.session.get("zoho_access_token")  # Get saved access token
    if not access_token:
        print("NO ACCESS TOKEN")
        return JsonResponse({"error": "Zoho OAuth required"}, status=401)

    print(f"ACCESS TOEKN : {access_token}")
    # Email details
    subject = "Order Confirmation"
    customer_email = "hmahmud01@gmail.com"
    owner_email = "hmahmud01@outlook.com"

    # Load email template
    context = {"customer_name": "John Doe", "order_id": "12345", "order_total": "$99"}
    html_message = render_to_string("emails/order_email.html", context)
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    # Send email to both customer & owner
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [customer_email, owner_email])

    return JsonResponse({"message": "Email sent successfully"})

def makepayment(request):
    post_data = request.POST
    print(f"POST : {post_data}")
    print(f"USERNAME : {request.user.username}")
    print(f"passwd : {request.user.password}")
    today_date = datetime.today().strftime('%Y%m%d')
    order = Order.objects.get(id=post_data['order'])
    order_trx_id = "meera-0"+str(order.id)+today_date
    charge = ShippingCharge.objects.get(type="local")
    total = order.get_cart_total + charge.charge
    print(f"TRX ID : {order_trx_id}")

    query_params = {
        "order_id": post_data['order'],
        "email": post_data['email'],
        "phone": post_data['phone'],
        "address": post_data['address'],
        "name": order.customer,
    }

    print("===========printing SSL RESPONSE ===================")
    # settings = { 'store_id': 'maise6244d4efe620f', 'store_pass': 'maise6244d4efe620f@ssl', 'issandbox': True }
    settings = { 'store_id': '	meeraseedcomloginnext0live', 'store_pass': '6674FB98173C235445', 'issandbox': False }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = total
    post_body['currency'] = "BDT"
    post_body['tran_id'] = order_trx_id
    # post_body['success_url'] = "http://meeraseed.com/success/"
    # post_body['fail_url'] = "http://meeraseed.com/failed/"
    # post_body['cancel_url'] = "http://meeraseed.com/failed/"
    # post_body['success_url'] = f"http://localhost/success/?{urlencode(query_params)}"
    # post_body['fail_url'] = f"http://localhost/failed/?{urlencode(query_params)}"
    # post_body['cancel_url'] = f"http://localhost/failed/?{urlencode(query_params)}"
    post_body['success_url'] = f"https://meeraseed.com/success/?{urlencode(query_params)}"
    post_body['fail_url'] = f"https://meeraseed.com/failed/?{urlencode(query_params)}"
    post_body['cancel_url'] = f"https://meeraseed.com/failed/?{urlencode(query_params)}"
    post_body['emi_option'] = 0
    post_body['cus_name'] = order.customer
    post_body['cus_email'] = post_data['email']
    post_body['cus_phone'] = post_data['phone']
    post_body['cus_add1'] = post_data['address']
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Meera Products"
    post_body['product_category'] = "Seed"
    post_body['product_profile'] = "agro products"


    response = sslcz.createSession(post_body)
    print(response)
    status = response['status']
        # <QueryDict: {'csrfmiddlewaretoken': ['Z9lL7jP7kSUTfxVm6cV1YsxpXG9UiCJr5p0RbrjMN7fC1DRd80t2tImxWCGcaOmn'],
    #              'bkash': ['07975686099'], 'pin': ['1234564'], 'order': [''], 'name': ['Hasan Mahmud'], 
    #              'address': ['shantinagar, dahat'], 'phone': ['01797568609'], 'email': ['hmahmud01@gmail.com']}>
    print(f"STATUS : {status}")
    # if status == "SUCCESS":
    #     order = Order.objects.get(id=post_data['order'])
    #     order.complete = True
    #     order.trx_id = order_trx_id

    #     print(f"order stat: {order.complete} {order.trx_id}")
    #     print(order)
    #     order.save()
    #     orderweb = OrderWeb(
    #         order = order,
    #         email = post_data['email'],
    #         phone = post_data['phone'],
    #         address = post_data['address'],
    #         payment_status = "PAID",
    #         name = post_data['name']
    #     )


    #     # SEND AN EMAIL FROM HERE
    #     orderweb.save()
    #     return redirect(response['GatewayPageURL'])
    # else:
    #     msg = response['failedreason']
    #     print(msg)
    #     order = Order.objects.get(id=post_data['order'])
    #     order.complete = False
    #     order.trx_id = order_trx_id

    #     print(f"order stat: {order.complete} {order.trx_id}")
    #     print(order)
    #     order.save()
    #     orderweb = OrderWeb.objects.get(order_id=order.id)
    #     orderweb.status = "FAILED",
    #     orderweb.payment_status = "UNABLE TO PAID: SSL ISSUE",
    #     # orderweb = OrderWeb(
    #     #     order = order,
    #     #     email = post_data['email'],
    #     #     phone = post_data['phone'],
    #     #     address = post_data['address'],
    #     #     status = "FAILED",
    #     #     payment_status = "UNABLE TO PAID: SSL ISSUE",
    #     #     name = post_data['name']
    #     # )

    #     # SEND AN EMAIL FROM HERE
    #     orderweb.save()
    #     return redirect('failedpage')
    return redirect(response['GatewayPageURL'])

def makeorder(request):
    print("====INSIDE MAKE====")
    post_data = request.POST
    print(post_data)
    order = Order.objects.get(id=post_data['order'])
    order.complete = True
    order.trx_id = "meera-"+str(order.id)
    # order.save()

    print(f"order stat: {order.complete} {order.trx_id}")
    print(order)
    # print(order_comp)
    order.save()
    print(order)
    orderweb = OrderWeb(
        order = order,
        email = post_data['email'],
        phone = post_data['phone'],
        address = post_data['address'],
        name = post_data['name']
    )
    orderweb.save()
    print("====ORDER WEB====")
    print(orderweb)
    return redirect('successpage')

@csrf_exempt
def successpage(request):
    order_id = request.GET.get('order_id')
    email = request.GET.get('email')
    phone = request.GET.get('phone')
    address = request.GET.get('address')
    name = request.GET.get('name')
    order = Order.objects.get(id=order_id)
    today_date = datetime.today().strftime('%Y%m%d')
    order_trx_id = "meera-0"+str(order.id)+today_date
    order.complete = True
    order.trx_id = order_trx_id

    print(f"order stat: {order.complete} {order.trx_id}")
    print(order)
    order.save()
    orderweb = OrderWeb(
        order = order,
        email = email,
        phone = phone,
        address = address,
        payment_status = "PAID",
        name = name
    )

    # SEND AN EMAIL FROM HERE

    email_data = {
        "status": "SUCCESS",
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "oid": order_id,
        "trx_id": order_trx_id
    }

    send_email_from_payment(email_data)
    print("SEND EMAIL FROM PAYMENT EXECUTED")

    orderweb.save()
    return render(request, 'web/success.html')
    # return render(request, 'home/homesuccess.html')

@csrf_exempt
def failedpage(request):
    order_id = request.GET.get('order_id')
    email = request.GET.get('email')
    phone = request.GET.get('phone')
    address = request.GET.get('address')
    name = request.GET.get('name')
    order = Order.objects.get(id=order_id)
    today_date = datetime.today().strftime('%Y%m%d')
    order_trx_id = "meera-0"+str(order.id)+today_date
    order.complete = True
    order.trx_id = order_trx_id

    print(f"order stat: {order.complete} {order.trx_id}")
    print(order)
    order.save()
    orderweb = OrderWeb(
        order = order,
        email = email,
        phone = phone,
        address = address,
        status = "FAILED",
        payment_status = "UNABLE TO PAID: SSL ISSUE",
        name = name
    )

    # SEND AN EMAIL FROM HERE
    orderweb.save()
    return render(request, 'web/failed.html')
    # return render(request, 'home/homefailed.html')

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
    if request.user.is_authenticated:
        customer = request.user.username
        print(f"{customer}")
    else:
        customer = "guest"
        print(f"{customer}")
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItems.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'remove-complete':
        orderItem.quantity = 0
    
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