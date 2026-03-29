
from django.contrib import admin
from .models import Course, Category, Login, Offer, Order

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'mrp', 'offer', 'stock', 'available', 'category']
    list_filter = ['category', 'available']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'offer_type', 'discount_percentage', 'start_date', 'end_date', 'active']
    list_filter = ['offer_type', 'active']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'created_at']
    list_filter = ['created_at']

@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = ['username', 'password']
    