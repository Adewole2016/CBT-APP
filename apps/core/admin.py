from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("profile_picture",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("profile_picture",)}),
    )

admin.site.register(User, CustomUserAdmin)
