from rest_framework import serializers
from .models import CartItem,Cart, Coupon, Order, OrderItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.FloatField(source='product.offer_price', read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'product_name', 'price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False)
    course = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(default=1)

    def validate(self, attrs):
        attrs['product_id'] = attrs.get('product_id') or attrs.get('course')
        if not attrs['product_id']:
            raise serializers.ValidationError("product_id or course is required")
        return attrs

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
    price = serializers.FloatField(source='product.offer_price', read_only=True)

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
        
