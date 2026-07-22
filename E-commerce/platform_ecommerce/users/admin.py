from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import SellerProfile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active", "created_at")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Platform role", {"fields": ("role", "phone_number")}),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "seller_type", "is_verified", "commission_rate", "user")
    list_filter = ("seller_type", "is_verified")
    search_fields = ("company_name", "tax_id", "user__username", "user__email")
