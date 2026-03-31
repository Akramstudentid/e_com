from rest_framework import serializers
from .models import CartItem,Cart, Coupon, Order, OrderItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.FloatField(source='product.price', read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'product_name', 'price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    
class CheckoutSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=50, required=False)
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    
class RemoveCartItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.FloatField(source='product.price', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'product_name', 'price']
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'discount_amount', 'final_price', 'created_at', 'items']
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_percent', 'active']
        