from os import name
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.urls.resolvers import URLPattern

from backend import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blankpage/', views.blankpage, name="blankpage"),
    path('login/', views.login, name="login"),
    path('verifylogin', views.verifyLogin, name="verifylogin"),
    path('userlogout/', views.userLogout, name="userlogout"),
    path('productcreate/', views.productCreate, name="productcreate"),
    path('savecategory/', views.saveCategory, name="savecategory"),
    path('savepacksize/', views.savePackSize, name="savepacksize"),
    path('savezone/', views.saveZone, name="savezone"),
    path('saveproduct/', views.saveProduct, name="saveproduct"),
    path('productlist/', views.productList, name="productlist"),
    path('productdetail/<int:pid>/', views.productDetail, name="productdetail"),
    path('statusupdate/<slug:state>/<int:pid>', views.statusUpdate, name="statusupdate"),
    path('stockupdate/<int:pid>', views.stockupdate, name="stockupdate"),
    path('orderlist/', views.orderList, name="orderlist"),
    path('orderdetail/<int:oid>/', views.orderDetail, name="orderdetail"),
    path('userindex/', views.userIndex, name="userindex"),
    path('userprofile/', views.userProfile, name="userprofile"),
    path('inventory/', views.inventory, name="inventory"),
    path('simulator/', views.simulator, name="simulator"),
    path('update_item/', views.updateItem, name='update_item'),
    path('cart/', views.cart, name='cart'),
    path('process_order/', views.processOrder, name='process_order')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
