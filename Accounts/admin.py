from django.contrib import admin


from .models import user, Profile, PasswordResetToken

@admin.register(user)
class userAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'password']
    search_fields = ['username', 'email']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'phone_number']
    search_fields = ['user__username', 'user__email']

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    


