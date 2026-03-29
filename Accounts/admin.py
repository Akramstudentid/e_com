from django.contrib import admin
from .models import user

@admin.register(user)
class userAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'password']
    search_fields = ['username', 'email']