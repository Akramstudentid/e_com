
from django.db import models
from django.contrib.auth.models import AbstractUser

class user(AbstractUser):

    email= models.EmailField(unique=True)

    address= models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.username

from django.utils import timezone
import random

class PasswordResetOTP(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))



class Profile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username



class PasswordResetToken(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds > 3600  # 1 hour
    