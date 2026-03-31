from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from decimal import Decimal

from django.core.mail import send_mail
from django.conf import settings

from Courses.models import Course
from drf_spectacular.utils import extend_schema

from .serializers import AddToCartSerializer, CartSerializer, ApplyCouponSerializer, CheckoutSerializer, SendOTPSerializer, UpdateCartItemSerializer, RemoveCartItemSerializer
from .models import Cart, CartItem, Coupon, Order, OrderItem

import random



class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)



@extend_schema(request=AddToCartSerializer)
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Course.objects.get(id=product_id)
        except Course.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        item.save()

        return Response({"message": "Added to cart"})


# ===================== UPDATE CART =====================

class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateCartItemSerializer
    

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']

        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()

        if not item:
            return Response({"error": "Item not found"}, status=404)

        item.quantity = quantity
        item.save()

        return Response({"message": "Cart updated"})


# ===================== REMOVE ITEM =====================

class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RemoveCartItemSerializer
    

    def delete(self, request, item_id):
        serializer = RemoveCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_id = serializer.validated_data['item_id']

        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()

        if not item:
            return Response({"error": "Item not found"}, status=404)

        item.delete()

        return Response({"message": "Item removed"})


# ===================== OTP =====================

OTP_STORE = {}  # Temporary storage


class SendOTPView(APIView):
    serializer_class = SendOTPSerializer
    
        
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if not email:
            return Response({"error": "Email is required"}, status=400)

        otp = str(random.randint(100000, 999999))
        OTP_STORE[email] = otp

        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            print("OTP SENT:", otp)

            return Response({"message": "OTP sent successfully"})
        except Exception as e:
            print("EMAIL ERROR:", e)
            return Response({"error": str(e)}, status=500)




class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplyCouponSerializer
    

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        try:
            coupon = Coupon.objects.get(code=code, active=True)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon"}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart)

        total = sum(item.product.price * item.quantity for item in items)
        discount = (coupon.discount_percent / 100) * total
        final_price = total - discount

        return Response({
            "total": total,
            "discount": discount,
            "final_price": final_price
        })


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon_code = serializer.validated_data.get('coupon_code')

        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart)

        total = sum(item.product.offer_price * item.quantity for item in items)  # use offer_price

        discount = 0
        coupon_code = request.data.get('coupon_code')
        if coupon_code:
            # try:
            #     coupon = Coupon.objects.get(code=coupon_code, active=True)
            #     discount = (coupon.discount_percent / 100) * total
            # except Coupon.DoesNotExist:
            #     return Response({"error": "Invalid coupon"}, status=400)
            pass

        # final_price = total - discount
        final_price = sum(item.product.offer_price * item.quantity for item in items)

        return Response({
            "total": total,
            "discount": discount,
            "final_price": final_price
        })