from rest_framework import serializers
from backend.models import *
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        depth = 1

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductZone
        fields = "__all__"
        depth = 1

class UserZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = "__all__"

User = get_user_model()

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password',
                  'first_name', 'last_name', 'email',)
        extra_kwargs = {'password': {"write_only": True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"

class CartProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = "__all__"
        depth = 1

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderApp
        fields = "__all__"
        # fields = ['id', 'email', 'phone', 'address', 'name', 'orderstatus']
        depth = 1