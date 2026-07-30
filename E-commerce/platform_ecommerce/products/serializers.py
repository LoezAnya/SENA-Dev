from PIL import Image
from rest_framework import serializers

from products.models import Product, ProductCategory, ProductVariant

# Sprint 2 image spec: max 3MB upload, target canvas 1340x1785 (Shein-style
# portrait product photo). Anything not already at that size gets
# resized/cropped to fit it exactly.
MAX_IMAGE_SIZE_BYTES = 3 * 1024 * 1024
TARGET_IMAGE_SIZE = (1340, 1785)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug", "parent", "is_active"]
        read_only_fields = ["id", "slug"]


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product",
            "color",
            "size",
            "sku",
            "stock",
            "price_override",
            "effective_price",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "effective_price", "created_at"]

    def validate_product(self, product):
        request = self.context.get("request")
        if request and product.seller_id != request.user.id:
            raise serializers.ValidationError(
                "You can only add variants to your own products."
            )
        return product


class ProductSerializer(serializers.ModelSerializer):
    """Seller-facing CRUD serializer.

    `seller` is set from the authenticated user in the view, never taken
    from client input, so a seller cannot create/edit a product on
    someone else's behalf.
    """

    variants = ProductVariantSerializer(many=True, read_only=True)
    seller = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "seller",
            "category",
            "name",
            "description",
            "base_price",
            "stock",
            "images",
            "is_active",
            "variants",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "seller", "images", "created_at", "updated_at"]

    def validate_base_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("base_price must be greater than 0.")
        return value


class ProductPublicSerializer(serializers.ModelSerializer):
    """Read-only representation exposed by the public catalog endpoint."""

    category = ProductCategorySerializer(read_only=True)
    seller_name = serializers.CharField(source="seller.seller_profile.company_name", read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "base_price",
            "category",
            "seller_name",
            "images",
            "variants",
            "created_at",
        ]


class ProductImageUploadSerializer(serializers.Serializer):
    """POST /api/v1/products/<id>/images/

    Validates size (<=3MB) and, on success, resizes/crops the image to
    the platform's canonical 1340x1785 canvas before storing it and
    appending its URL to Product.images.
    """

    image = serializers.ImageField()

    def validate_image(self, file):
        if file.size > MAX_IMAGE_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Image must be at most {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB "
                f"(got {file.size / (1024 * 1024):.2f}MB)."
            )
        try:
            with Image.open(file) as img:
                img.verify()
        except Exception as exc:  # noqa: BLE001 - want to surface any PIL error
            raise serializers.ValidationError("File is not a valid image.") from exc
        file.seek(0)
        return file
