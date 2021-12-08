from django.db.models import manager, query
from django.shortcuts import render
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
        query = Product.objects.all()
        serializer = ProductSerializer(query, many=True)
        data = []
        for product in serializer.data:
            print(product)
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
                print("Single Product favourite once")
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