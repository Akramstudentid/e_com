from django.db import models
from django.conf import settings
from Courses.models import Course


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.user.username if self.user else 'Anonymous'}"


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Course, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_orders"
    )
    total_price = models.FloatField()
    discount_amount = models.FloatField(default=0)
    final_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Course, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"