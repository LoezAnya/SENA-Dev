from django.contrib import admin

from products.models import Product, ProductCategory, ProductVariant


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active")
    prepopulated_fields = {"slug": ("name",)}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "seller", "category", "base_price", "stock", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name", "seller__username")
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "color", "size", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("sku", "product__name")
