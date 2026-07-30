import hashlib
import io
import uuid

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from PIL import Image, ImageOps
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from products.filters import ProductFilter
from products.models import Product, ProductVariant
from products.permissions import IsProductOwner
from products.serializers import (
    ProductImageUploadSerializer,
    ProductPublicSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    TARGET_IMAGE_SIZE,
)
from users.permissions import IsSeller

CATALOG_CACHE_TTL_SECONDS = 60 * 5  # 5 minutes, per Sprint 2 spec
CATALOG_CACHE_PREFIX = "catalog:list:"


# ---------------------------------------------------------------------------
# Seller-facing CRUD (own products only)
# ---------------------------------------------------------------------------
class SellerProductViewSet(viewsets.ModelViewSet):
    """Full CRUD for the authenticated seller's own products.

    /api/v1/products/mine/            GET, POST
    /api/v1/products/mine/{id}/       GET, PUT, PATCH, DELETE
    """

    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller, IsProductOwner]

    def get_queryset(self):
        return (
            Product.objects.select_related("category", "seller")
            .prefetch_related("variants")
            .filter(seller=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
        _invalidate_catalog_cache()

    def perform_update(self, serializer):
        serializer.save()
        _invalidate_catalog_cache()

    def perform_destroy(self, instance):
        instance.delete()
        _invalidate_catalog_cache()


class SellerProductVariantViewSet(viewsets.ModelViewSet):
    """Full CRUD for variants, scoped to the authenticated seller's products.

    /api/v1/products/mine/variants/           GET, POST
    /api/v1/products/mine/variants/{id}/      GET, PUT, PATCH, DELETE
    """

    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller, IsProductOwner]

    def get_queryset(self):
        return ProductVariant.objects.select_related("product").filter(
            product__seller=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()
        _invalidate_catalog_cache()

    def perform_update(self, serializer):
        serializer.save()
        _invalidate_catalog_cache()

    def perform_destroy(self, instance):
        instance.delete()
        _invalidate_catalog_cache()


class ProductImageUploadView(APIView):
    """POST /api/v1/products/mine/{id}/images/

    Validates (<=3MB, valid image), resizes/crops to the platform's
    canonical 1340x1785 canvas with Pillow, stores the file, and appends
    its URL to Product.images.
    """

    permission_classes = [permissions.IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def get_product(self, request, pk):
        return generics.get_object_or_404(
            Product.objects.filter(seller=request.user), pk=pk
        )

    def post(self, request, pk):
        product = self.get_product(request, pk)
        serializer = ProductImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded = serializer.validated_data["image"]

        resized_bytes = _resize_to_canvas(uploaded, TARGET_IMAGE_SIZE)
        filename = f"products/{product.id}/{uuid.uuid4().hex}.jpg"
        saved_path = default_storage.save(filename, ContentFile(resized_bytes))
        image_url = default_storage.url(saved_path)

        product.images = [*product.images, image_url]
        product.save(update_fields=["images", "updated_at"])
        _invalidate_catalog_cache()

        return Response(
            {"images": product.images}, status=status.HTTP_201_CREATED
        )


def _resize_to_canvas(uploaded_file, target_size):
    """Resize+crop (centered) an uploaded image to exactly target_size,
    re-encoded as JPEG, returned as raw bytes.
    """
    with Image.open(uploaded_file) as img:
        img = img.convert("RGB")
        fitted = ImageOps.fit(img, target_size, method=Image.LANCZOS)
        buffer = io.BytesIO()
        fitted.save(buffer, format="JPEG", quality=88)
        return buffer.getvalue()


# ---------------------------------------------------------------------------
# Public catalog (buyer-facing, read-only, cached)
# ---------------------------------------------------------------------------
class PublicProductListView(generics.ListAPIView):
    """GET /api/v1/products/

    Public, paginated product listing with filters:
    - ?category=<id-or-slug>
    - ?min_price=&max_price=
    - ?search=<text>            (name, description)
    - ?ordering=base_price|-base_price|created_at|-created_at

    Results are cached in Redis per unique query string for 5 minutes.
    """

    serializer_class = ProductPublicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["base_price", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Product.objects.select_related("category", "seller__seller_profile")
            .prefetch_related("variants")
            .filter(is_active=True)
        )

    def list(self, request, *args, **kwargs):
        cache_key = _catalog_cache_key(request)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=CATALOG_CACHE_TTL_SECONDS)
        return response


class PublicProductDetailView(generics.RetrieveAPIView):
    """GET /api/v1/products/{id}/ — public product detail (no cache)."""

    serializer_class = ProductPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.filter(is_active=True).select_related(
        "category", "seller__seller_profile"
    ).prefetch_related("variants")


def _catalog_cache_key(request):
    # Deliberately NOT hashed: _invalidate_catalog_cache() below needs to
    # glob-match on CATALOG_CACHE_PREFIX, and a hash would hide it. Query
    # strings are bounded in practice (filters + pagination), so key
    # length isn't a real concern here.
    query_hash = hashlib.sha256(request.get_full_path().encode()).hexdigest()[:16]
    return f"{CATALOG_CACHE_PREFIX}{query_hash}"


def _invalidate_catalog_cache():
    """Sprint 2 keeps invalidation simple: clear every cached catalog page
    whenever a product/variant is created, updated, deleted, or gets a
    new image. A more surgical per-key invalidation (e.g. tracking keys
    in a Redis set) is a reasonable optimization for a later sprint once
    traffic patterns are known; for now correctness > cache-hit-ratio.
    """
    if hasattr(cache, "delete_pattern"):
        cache.delete_pattern(f"{CATALOG_CACHE_PREFIX}*")
    else:
        cache.clear()
