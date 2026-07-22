"""
Sprint 1 test suite.

Covers:
- User / SellerProfile model behaviour.
- Registration (buyer + seller) via the API.
- Login (JWT obtain) + token refresh.
- /me/ endpoint auth requirement and payload shape.
- Basic rate-limiting behaviour on register/login.

Run with:
    pytest --cov=users --cov-report=term-missing
or:
    python manage.py test users
"""
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import SellerProfile, User


class UserModelTests(TestCase):
    def test_create_buyer_user(self):
        user = User.objects.create_user(
            username="buyer1", email="buyer1@example.com", password="StrongPass123"
        )
        self.assertEqual(user.role, User.Role.BUYER)
        self.assertTrue(user.is_buyer)
        self.assertFalse(user.is_seller)
        self.assertTrue(user.check_password("StrongPass123"))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="root", email="root@example.com", password="StrongPass123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, User.Role.ADMIN)

    def test_email_is_unique(self):
        User.objects.create_user(
            username="u1", email="dup@example.com", password="StrongPass123"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="u2", email="dup@example.com", password="StrongPass123"
            )


class SellerProfileModelTests(TestCase):
    def test_seller_profile_promotes_user_role(self):
        user = User.objects.create_user(
            username="seller1",
            email="seller1@example.com",
            password="StrongPass123",
            role=User.Role.BUYER,  # starts as buyer on purpose
        )
        profile = SellerProfile.objects.create(
            user=user,
            company_name="Acme Fashion",
            tax_id="TAX-12345",
            seller_type=SellerProfile.SellerType.THIRD_PARTY,
        )
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.SELLER)
        self.assertEqual(str(profile), "Acme Fashion (3P)")

    def test_tax_id_must_be_unique(self):
        u1 = User.objects.create_user(username="s1", email="s1@example.com", password="StrongPass123")
        u2 = User.objects.create_user(username="s2", email="s2@example.com", password="StrongPass123")
        SellerProfile.objects.create(
            user=u1, company_name="A", tax_id="TAX-999", seller_type="3P"
        )
        with self.assertRaises(Exception):
            SellerProfile.objects.create(
                user=u2, company_name="B", tax_id="TAX-999", seller_type="3P"
            )


class RegistrationAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.register_url = reverse("users:register")

    def test_register_buyer_success(self):
        payload = {
            "username": "newbuyer",
            "email": "newbuyer@example.com",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
            "role": "buyer",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "buyer")
        self.assertTrue(User.objects.filter(username="newbuyer").exists())

    def test_register_seller_requires_company_fields(self):
        payload = {
            "username": "newseller",
            "email": "newseller@example.com",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
            "role": "seller",
            # company_name / tax_id / seller_type intentionally omitted
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company_name", response.data)

    def test_register_seller_success_creates_profile(self):
        payload = {
            "username": "sellerok",
            "email": "sellerok@example.com",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
            "role": "seller",
            "company_name": "Fast Fashion Co",
            "tax_id": "TAX-777",
            "seller_type": "FBP",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="sellerok")
        self.assertTrue(SellerProfile.objects.filter(user=user).exists())
        self.assertEqual(user.seller_profile.seller_type, "FBP")

    def test_register_password_mismatch(self):
        payload = {
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password": "StrongPass123",
            "password_confirm": "DifferentPass123",
            "role": "buyer",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)


class AuthFlowAPITests(APITestCase):
    """End-to-end: register -> login -> obtain JWT -> access /me/."""

    def setUp(self):
        cache.clear()
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.me_url = reverse("users:me")
        self.refresh_url = reverse("token_refresh")

        self.client.post(
            self.register_url,
            {
                "username": "authuser",
                "email": "authuser@example.com",
                "password": "StrongPass123",
                "password_confirm": "StrongPass123",
                "role": "buyer",
            },
            format="json",
        )

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            self.login_url,
            {"username": "authuser", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {"username": "authuser", "password": "WrongPass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_profile_with_valid_token(self):
        login_response = self.client.post(
            self.login_url,
            {"username": "authuser", "password": "StrongPass123"},
            format="json",
        )
        access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "authuser")
        self.assertIsNone(response.data["seller_profile"])

    def test_token_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            self.login_url,
            {"username": "authuser", "password": "StrongPass123"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class RateLimitTests(APITestCase):
    """Confirms the API-gateway-style rate limit on /register/ engages."""

    def setUp(self):
        cache.clear()
        self.register_url = reverse("users:register")

    def test_register_rate_limit_blocks_after_threshold(self):
        # RATELIMIT rate for register is 10/m; fire 11 requests from the
        # same IP and expect the 11th to be throttled with 429.
        last_status = None
        for i in range(11):
            payload = {
                "username": f"rl_user_{i}",
                "email": f"rl_user_{i}@example.com",
                "password": "StrongPass123",
                "password_confirm": "StrongPass123",
                "role": "buyer",
            }
            response = self.client.post(self.register_url, payload, format="json")
            last_status = response.status_code
        self.assertEqual(last_status, status.HTTP_429_TOO_MANY_REQUESTS)
