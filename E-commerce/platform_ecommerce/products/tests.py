"""
Sprint 2 test suite additions.

Covers:
- ProductCategory / ProductVariant model behaviour.
- Seller CRUD on /api/v1/products/mine/ — ownership enforced (a seller
  can never see/edit/delete another seller's product).
- Image upload validation (size limit) + resize-to-canvas pipeline.
- Public catalog: filters (category, price range, search), pagination,
  and Redis cache hit/invalidation behaviour.

Run with:
    python manage.py test products
or:
    pytest --cov=products --cov-report=term-missing
"""
import io

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Product, ProductCategory, ProductVariant
from users.models import SellerProfile, User


def make_seller(username, tax_id, seller_type="3P"):
    user = User.objects.create_user(
        username=username, email=f"{username}@example.com", password="StrongPass123"
    )
    SellerProfile.objects.create(
        user=user, company_name=f"{username} Co", tax_id=tax_id, seller_type=seller_type
    )
    return user


def make_buyer(username):
    return User.objects.create_user(
        username=username, email=f"{username}@example.com", password="StrongPass123"
    )


def in_memory_image(width=800, height=1200, fmt="JPEG", size_bytes_pad=0):
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(200, 50, 50)).save(buf, format=fmt)
    if size_bytes_pad:
        buf.write(b"0" * size_bytes_pad)
    buf.seek(0)
    buf.name = "test.jpg"
    return buf


class ProductCategoryModelTests(TestCase):
    def test_slug_auto_generated(self):
        category = ProductCategory.objects.create(name="Women's Dresses")
        self.assertEqual(category.slug, "womens-dresses")


class ProductModelTests(TestCase):
    def setUp(self):
        self.seller_user = make_seller("catseller", "TAX-001")
        self.category = ProductCategory.objects.create(name="Tops")

    def test_create_product(self):
        product = Product.objects.create(
            seller=self.seller_user,
            category=self.category,
            name="Basic Tee",
            description="A basic cotton tee.",
            base_price="9.99",
            stock=100,
            images=["https://cdn.example.com/img1.jpg"],
        )
        self.assertTrue(product.is_active)
        self.assertEqual(str(product), "Basic Tee")
        self.assertEqual(product.seller.role, User.Role.SELLER)


class ProductVariantModelTests(TestCase):
    def setUp(self):
        self.seller_user = make_seller("varseller", "TAX-002")
        self.category = ProductCategory.objects.create(name="Dresses")
        self.product = Product.objects.create(
            seller=self.seller_user,
            category=self.category,
            name="Summer Dress",
            base_price="29.99",
            stock=50,
        )

    def test_effective_price_falls_back_to_base_price(self):
        variant = ProductVariant.objects.create(
            product=self.product, color="Red", size="M", sku="SD-RED-M", stock=10
        )
        self.assertEqual(variant.effective_price, self.product.base_price)

    def test_effective_price_uses_override(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            color="Blue",
            size="L",
            sku="SD-BLUE-L",
            stock=5,
            price_override="24.99",
        )
        self.assertEqual(str(variant.effective_price), "24.99")

    def test_unique_variant_per_product_color_size(self):
        ProductVariant.objects.create(
            product=self.product, color="Red", size="S", sku="SD-RED-S", stock=1
        )
        with self.assertRaises(Exception):
            ProductVariant.objects.create(
                product=self.product, color="Red", size="S", sku="SD-RED-S-2", stock=1
            )


class SellerProductCRUDAPITests(APITestCase):
    """Ownership is the core Sprint 2 rule: a seller only ever sees/edits
    their own catalog through /api/v1/products/mine/.
    """

    def setUp(self):
        cache.clear()
        self.category = ProductCategory.objects.create(name="Accessories")
        self.seller_a = make_seller("sellerA", "TAX-A1")
        self.seller_b = make_seller("sellerB", "TAX-B1")
        self.buyer = make_buyer("buyer1")

        self.product_a = Product.objects.create(
            seller=self.seller_a,
            category=self.category,
            name="Seller A Bag",
            base_price="15.00",
            stock=10,
        )
        self.list_url = reverse("products:my-product-list")

    def authenticate(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    def test_buyer_cannot_create_product(self):
        self.authenticate(self.buyer)
        response = self.client.post(
            self.list_url,
            {"category": self.category.id, "name": "Not allowed", "base_price": "5.00", "stock": 1},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seller_creates_own_product(self):
        self.authenticate(self.seller_a)
        response = self.client.post(
            self.list_url,
            {"category": self.category.id, "name": "New Hat", "base_price": "12.50", "stock": 20},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["seller"], self.seller_a.id)

    def test_seller_list_only_shows_own_products(self):
        Product.objects.create(
            seller=self.seller_b, category=self.category, name="Seller B Shoes",
            base_price="40.00", stock=5,
        )
        self.authenticate(self.seller_a)
        response = self.client.get(self.list_url)
        names = [p["name"] for p in response.data["results"]]
        self.assertIn("Seller A Bag", names)
        self.assertNotIn("Seller B Shoes", names)

    def test_seller_cannot_retrieve_another_sellers_product(self):
        self.authenticate(self.seller_b)
        detail_url = reverse("products:my-product-detail", args=[self.product_a.id])
        response = self.client.get(detail_url)
        # Not in seller_b's queryset at all -> 404, not 403 (no leakage of existence)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_seller_cannot_delete_another_sellers_product(self):
        self.authenticate(self.seller_b)
        detail_url = reverse("products:my-product-detail", args=[self.product_a.id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(id=self.product_a.id).exists())

    def test_seller_updates_own_product(self):
        self.authenticate(self.seller_a)
        detail_url = reverse("products:my-product-detail", args=[self.product_a.id])
        response = self.client.patch(detail_url, {"name": "Renamed Bag"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_a.refresh_from_db()
        self.assertEqual(self.product_a.name, "Renamed Bag")


class ProductImageUploadAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.category = ProductCategory.objects.create(name="Shoes")
        self.seller = make_seller("imgseller", "TAX-IMG")
        self.product = Product.objects.create(
            seller=self.seller, category=self.category, name="Sneakers",
            base_price="60.00", stock=15,
        )
        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        self.upload_url = reverse("products:my-product-images", args=[self.product.id])

    def test_upload_valid_image_resizes_and_appends_url(self):
        image_file = in_memory_image(width=800, height=1000)
        response = self.client.post(
            self.upload_url, {"image": image_file}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["images"]), 1)

    def test_upload_rejects_oversized_image(self):
        # Pad well past the 3MB ceiling.
        oversized = in_memory_image(width=100, height=100, size_bytes_pad=3 * 1024 * 1024 + 1)
        response = self.client.post(
            self.upload_url, {"image": oversized}, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", response.data)


class PublicCatalogAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.cat_tops = ProductCategory.objects.create(name="Tops")
        self.cat_bottoms = ProductCategory.objects.create(name="Bottoms")
        seller = make_seller("pubseller", "TAX-PUB")

        Product.objects.create(
            seller=seller, category=self.cat_tops, name="Cheap Tee",
            base_price="5.00", stock=100,
        )
        Product.objects.create(
            seller=seller, category=self.cat_tops, name="Premium Tee",
            base_price="45.00", stock=10,
        )
        Product.objects.create(
            seller=seller, category=self.cat_bottoms, name="Jeans",
            base_price="35.00", stock=20,
        )
        self.list_url = reverse("products:public-list")

    def test_list_is_paginated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

    def test_filter_by_category_slug(self):
        response = self.client.get(self.list_url, {"category": self.cat_bottoms.slug})
        names = [p["name"] for p in response.data["results"]]
        self.assertEqual(names, ["Jeans"])

    def test_filter_by_price_range(self):
        response = self.client.get(self.list_url, {"min_price": 10, "max_price": 40})
        names = sorted(p["name"] for p in response.data["results"])
        self.assertEqual(names, ["Jeans"])

    def test_search_by_name(self):
        response = self.client.get(self.list_url, {"search": "premium"})
        names = [p["name"] for p in response.data["results"]]
        self.assertEqual(names, ["Premium Tee"])

    def test_inactive_products_excluded(self):
        Product.objects.filter(name="Jeans").update(is_active=False)
        response = self.client.get(self.list_url)
        names = [p["name"] for p in response.data["results"]]
        self.assertNotIn("Jeans", names)


class CatalogCacheTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.category = ProductCategory.objects.create(name="Cached Cat")
        self.seller = make_seller("cacheseller", "TAX-CACHE")
        self.product = Product.objects.create(
            seller=self.seller, category=self.category, name="Cached Item",
            base_price="10.00", stock=5,
        )
        self.list_url = reverse("products:public-list")

    def test_second_request_is_served_from_cache(self):
        first = self.client.get(self.list_url)
        self.assertEqual(len(first.data["results"]), 1)

        # Mutate the DB directly (bypassing the view, so no cache
        # invalidation happens) — a cached second response should still
        # reflect the stale, cached state.
        Product.objects.create(
            seller=self.seller, category=self.category, name="Added After Cache",
            base_price="11.00", stock=1,
        )
        second = self.client.get(self.list_url)
        self.assertEqual(len(second.data["results"]), 1)  # still cached

    def test_cache_invalidated_on_seller_create(self):
        from rest_framework_simplejwt.tokens import RefreshToken

        first = self.client.get(self.list_url)
        self.assertEqual(len(first.data["results"]), 1)

        token = RefreshToken.for_user(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        self.client.post(
            reverse("products:my-product-list"),
            {"category": self.category.id, "name": "Fresh Item", "base_price": "9.00", "stock": 3},
        )
        self.client.credentials()  # clear auth for the public request below

        third = self.client.get(self.list_url)
        self.assertEqual(len(third.data["results"]), 2)
