from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ProductCategory(models.Model):
    """Simple, potentially self-nested category tree."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_categories"
        verbose_name_plural = "Product categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Base catalog entry, owned by a seller.

    Variants (color/size) are modeled separately (ProductVariant) starting
    Sprint 2; this base model holds only the fields needed for Sprint 1's
    data model milestone.
    """

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={"role": "seller"},
    )
    category = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    images = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["seller"]),
            models.Index(fields=["category"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    """A purchasable variation of a Product (e.g. Red / M).

    Each variant carries its own stock and an optional price override;
    when price_override is null, the variant is sold at the parent
    Product's base_price.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    sku = models.CharField(max_length=64, unique=True)
    stock = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_variants"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "color", "size"], name="unique_variant_per_product"
            )
        ]
        indexes = [models.Index(fields=["sku"])]

    def __str__(self):
        return f"{self.product.name} — {self.color}/{self.size}".strip()

    @property
    def effective_price(self):
        return (
            self.price_override
            if self.price_override is not None
            else self.product.base_price
        )
