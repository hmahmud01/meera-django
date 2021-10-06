from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from backend.models import Category, Product, ProductImage, ProductZone, Zone

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
    return render(request, "products/create.html", {"categories": categories, "zones": zones})


def saveCategory(request):
    print(request)
    print(request.POST)
    data = request.POST
    category = Category(
        title = data['title']
    )
    category.save()
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
    
    product = Product(
        name=post_data['name'],
        category=category,
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
    return render(request, "orders/index.html")

def userIndex(request):
    return render(request, "users/index.html")

def userProfile(request):
    return render(request, "users/profile.html")

def inventory(request):
    return render(request, "inventory/index.html")
