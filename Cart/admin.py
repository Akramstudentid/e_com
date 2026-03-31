from django.contrib import admin

from Cart.models import Cart, CartItem, Coupon, Order, OrderItem

# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_filter = ['created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']
    list_filter = ['cart']
    
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):    
    list_display = ['code', 'discount_percent', 'active']
    list_filter = ['active']
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): 
    list_display = ['user', 'total_price', 'discount_amount', 'final_price', 'created_at']
    list_filter = ['created_at']
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
    list_filter = ['order']

    
    
