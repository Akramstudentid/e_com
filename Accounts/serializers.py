# serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)
    live_location = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'address',
            'live_location',
            'phone_number'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        confirm_password = attrs.pop('confirm_password', None)
        live_location = attrs.pop('live_location', None)

        if confirm_password is not None and attrs.get('password') != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if live_location and not attrs.get('address'):
            attrs['address'] = live_location

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(min_length=6)
