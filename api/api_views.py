from django.db.models import manager, query
from django.shortcuts import render
import api
from backend.views import cart
from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from backend.models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class ListProductAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CreateProductAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class UpdateProductAPIView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class DeleteProductAPIView(DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# CUSTOM VIEWS
class ProductView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        query = Product.objects.filter(status=True)
        serializer = ProductSerializer(query, many=True)
        data = []
        for product in serializer.data:
            # print(product)
            fav_query = Favourite.objects.filter(user=request.user).filter(product_id=product['id'])
            if fav_query:
                product['favourite'] = fav_query[0].isFavourite
            else:
                product['favourite'] = False
            zone = ProductZone.objects.filter(product=product['id'])
            zonelist = []
            for z in zone:
                zonelist.append(z.zone.name)            
            product['zonelist'] = zonelist
            data.append(product)
        return Response(data)

class FavouriteView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        user = request.user
        product_id = request.data['id']

        try:
            product = Product.objects.get(id=product_id)
            single_favourite_product = Favourite.objects.filter(user=user).filter(product=product).first()
            if single_favourite_product:
                fav_status = single_favourite_product.isFavourite
                single_favourite_product.isFavourite = not fav_status
                single_favourite_product.save()
            else:
                Favourite.objects.create(product=product, user=user, isFavourite=True)
            response_msg = {'error': False}
        except:
            response_msg = {'error': True}
        
        return Response(response_msg)

class RegisterView(APIView):
    def post(self, request):
        post_data = request.data
        # {'username': '111', 'password': '1111', 'name': 'user', 'phone': '111', 'jela': 'jela', 'upojela': 'upojela'}
        print(post_data)
        print(post_data['username'])
        serializers = Userserializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({"Error": False})
        return Response({"Error": True})

class CartView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        user = request.user
        try:
            cart_obj = Cart.objects.filter(user=user).filter(isComplete=False)
            data = []
            cart_serializer = CartSerializer(cart_obj, many=True)
            for cart in cart_serializer.data:
                cart_product_obj = CartProduct.objects.filter(cart=cart["id"])
                cart_product_obj_serializer = CartProductSerializers(
                    cart_product_obj, many=True)
                cart['cartproducts'] = cart_product_obj_serializer.data
                data.append(cart)

            response_msg = {"error": False, "data": data}
        except:
            response_msg = {"error": True, "data": "No Data"}
        return Response(response_msg)        


class OrderView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        
        try:
            data = []
            query = OrderApp.objects.filter(cart__user=request.user)            
            serializers = OrderSerializer(query, many=True)

            # print(serializers.data)
            for order in serializers.data:
                order_remark = ""
                orderapp = OrderApp.objects.get(id=order['id'])
                # print(orderapp.phone)
                orderstatus = Orderstatus.objects.filter(order_id=order['id'])                
                if orderstatus is not []:
                    for status in orderstatus:                    
                        if status.remark is not None:
                            order_remark += status.remark
                        else:
                            order_remark = "Under Process"
                else:
                    order_remark = "Under Process"
                
                cart_products = CartProduct.objects.filter(cart=order['cart']['id'])
                cart_product_obj_serializer = CartProductSerializers(
                    cart_products, many=True)                
                order['cart']['cartproducts'] = cart_product_obj_serializer.data
                # print(cart_product_obj_serializer.data)
                # print("check")
                # print("custom data")
                cart_data = cart_product_obj_serializer.data
                cartproducts = []
                # for data in cart_data:
                #     products = []
                #     for product in data['product']:
                #         item_product = Product.objects.get(id=product['id'])
                #         item_serializer = ProductSerializer(item_product)
                #         products.append(item_serializer.data)                        
                #     data['product'] = products
                #     print(data)
                #     cartproducts.append(data)
                # print(cartproducts)
                # order['cart']['cartproducts'] = cartproducts
                order['cart']['cartproducts'] = cart_product_obj_serializer.data
                order['remark'] = order_remark
                data.append(order)
            print("printing order view")

            # print(data)
            response_msg = {"error": False, "data": data}
        except:
            data = []
            response_msg = {"error": True, "data": data}
        return Response(response_msg)

class AddToCart(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        
        product_id = request.data['id']
        product_qty = request.data['qty']
        product_obj = Product.objects.get(id=product_id)
        # print(product_obj, "product_obj")

        cart_cart = Cart.objects.filter(
            user=request.user).filter(isComplete=False).first()
        cart_product_obj = CartProduct.objects.filter(
            product__id=product_id).first()

        try:
            if cart_cart:
                print(cart_cart)
                print("OLD CART")
                this_product_in_cart = cart_cart.cartproduct_set.filter(
                    product=product_obj)
                if this_product_in_cart.exists():
                    cartprod_uct = CartProduct.objects.filter(
                        product=product_obj).filter(cart__isComplete=False).first()
                    cartprod_uct.quantity = product_qty
                    cartprod_uct.subtotal += product_obj.price * product_qty
                    total_qty = cartprod_uct.quantity * product_obj.pack_size.qty
                    print("total qty")
                    print(total_qty)
                    print(product_obj.disc_price)
                    discount_price = 0
                    if total_qty >= 500.0:
                        print("if")
                        discount_price = cartprod_uct.subtotal * product_obj.disc_price / 100
                        print(discount_price)                    
                    else:
                        print("else")                                       
                    cartprod_uct.subtotal = cartprod_uct.subtotal - discount_price
                    cartprod_uct.subtotal = round(cartprod_uct.subtotal, 2)
                    cartprod_uct.save()
                    cart_total_price = product_obj.price * product_qty
                    cart_cart.total += cartprod_uct.subtotal
                    cart_cart.save()
                else:
                    print("NEW CART PRODUCT CREATED--OLD CART")
                    cart_product_new = CartProduct.objects.create(
                        cart=cart_cart,
                        price=product_obj.price,
                        quantity=product_qty,
                        subtotal=product_obj.price * product_qty
                    )
                    cart_product_new.product.add(product_obj)
                    cart_total_price = product_obj.price * product_qty
                    print(cart_total_price)
                    cart_cart.total += cart_total_price
                    # cart_cart.total += product_obj.price
                    cart_cart.save()
            else:
                Cart.objects.create(user=request.user,
                                    total=0.0, isComplete=False)
                new_cart = Cart.objects.filter(
                    user=request.user).filter(isComplete=False).first()
                cart_product_new = CartProduct.objects.create(
                    cart=new_cart,
                    price=product_obj.price,
                    quantity=product_qty,
                    subtotal=product_obj.price * product_qty
                )
                cart_product_new.product.add(product_obj)
                cart_total_price = product_obj.price * product_qty
                print(cart_total_price)
                new_cart.total += cart_total_price
                new_cart.save()
            response_mesage = {
                'error': False, 'message': "Product add to card successfully", "productid": product_id}
        except:
            response_mesage = {'error': True,
                               'message': "Product Not add!Somthing is Wromg"}
        return Response(response_mesage)


class DeleteCartProduct(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        cart_product_id = request.data['id']
        try:
            cart_product_obj = CartProduct.objects.get(id=cart_product_id)
            cart_cart = Cart.objects.filter(
                user=request.user).filter(isComplete=False).first()
            cart_cart.total -= cart_product_obj.subtotal
            cart_product_obj.delete()
            cart_cart.save()
            response_msg = {'error': False}
        except:
            response_msg = {'error': True}
        return Response(response_msg)


class DeleteCart(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        cart_id = request.data['id']
        try:
            cart_obj = Cart.objects.get(id=cart_id)
            cart_obj.delete()
            response_msg = {'error': False}
        except:
            response_msg = {'error': True}
        return Response(response_msg)

class Order(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(relf, request):
        try:
            data = request.data
            # print(data)
            cart_id = data['cartid']
            address = data['address']
            email = data['email']
            phone = data['phone']
            name = data['name']
            cart_obj = Cart.objects.get(id=cart_id)
            cart_obj.isComplete = True
            cart_obj.save()

            order = OrderApp.objects.create(
                cart=cart_obj,
                email=email,
                address=address,
                phone=phone,
                name=name
            )

            Orderstatus.objects.create(
                order=order,
                status="Ordered Now",
                remark="Your Order Is In Progress"
            )
            
            cart_products = CartProduct.objects.filter(cart__id=cart_id)
            for cart_product in cart_products:
                qty = cart_product.quantity                
                items = cart_product.product.all()
                for item in items:                    
                    p = Product.objects.get(id=item.id)
                    p.inv_stock = p.inv_stock - qty                    
                    p.save()
            
            response_msg = {"error": False, "message": "Your Order is Completed"}
        except:
            response_msg = {"error": True, "message": "Somthing is Wrong !"}
        return Response(response_msg)

class CategoryView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        query = Category.objects.all()
        serializer = CategorySerializer(query, many=True)
        return Response(serializer.data)