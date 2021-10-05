from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, "index.html")

def blankpage(request):
    return render(request, "sample.html")

def login(request):
    return render(request, "login.html")

def productCreate(request):
    return render(request, "products/create.html")

def productList(request):
    return render(request, "products/list.html")

def productDetail(request):
    return render(request, "products/detail.html")

def orderList(request):
    return render(request, "orders/index.html")

def userIndex(request):
    return render(request, "users/index.html")

def userProfile(request):
    return render(request, "users/profile.html")

def inventory(request):
    return render(request, "inventory/index.html")
