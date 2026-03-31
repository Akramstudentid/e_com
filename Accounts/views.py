# accounts/views.py
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema

from .models import PasswordResetOTP
from .serializers import RegisterSerializer, SendOTPSerializer, VerifyOTPSerializer

User = get_user_model()



@extend_schema(request=RegisterSerializer)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User created"}, status=201)

@extend_schema(request=SendOTPSerializer)
class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "If email exists, OTP sent"}, status=200)

        PasswordResetOTP.objects.filter(user=user).delete()

        otp = PasswordResetOTP.generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_mail(
            "Password Reset OTP",
            f"Your OTP is {otp}",
            "noreply@example.com",
            [email],
        )

        return Response({"message": "OTP sent"})

@extend_schema(request=SendOTPSerializer)
class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "If email exists, OTP sent"}, status=200)

        PasswordResetOTP.objects.filter(user=user).delete()

        otp = PasswordResetOTP.generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_mail(
            "Password Reset OTP",
            f"Your OTP is {otp}",
            "noreply@example.com",
            [email],
        )

        return Response({"message": "OTP sent"})
    
@extend_schema(request=VerifyOTPSerializer)
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        password = serializer.validated_data['password']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Invalid email"}, status=400)

        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).last()

        if not otp_obj:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        user.password = make_password(password)
        user.save()

        otp_obj.delete()

        return Response({"message": "Password reset successful"})