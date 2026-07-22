from django.test import TestCase

from products.models import Product, ProductCategory
from users.models import SellerProfile, User


class ProductCategoryModelTests(TestCase):
    def test_slug_auto_generated(self):
        category = ProductCategory.objects.create(name="Women's Dresses")
        self.assertEqual(category.slug, "womens-dresses")


class ProductModelTests(TestCase):
    def setUp(self):
        self.seller_user = User.objects.create_user(
            username="catseller", email="catseller@example.com", password="StrongPass123"
        )
        SellerProfile.objects.create(
            user=self.seller_user,
            company_name="Cat Fashion",
            tax_id="TAX-001",
            seller_type="3P",
        )
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
