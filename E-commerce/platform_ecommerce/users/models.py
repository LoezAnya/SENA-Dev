from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.managers import UserManager


class User(AbstractUser):
    """Platform user, extended with an explicit role.

    Role determines which part of the platform the user can operate in:
    - buyer: shops and places orders.
    - seller: manages a SellerProfile + catalog (see SellerProfile.seller_type
      for the 3P / FBP / OEM distinction).
    - admin: internal platform staff (superuser flag is separate from this).
    """

    class Role(models.TextChoices):
        BUYER = "buyer", "Buyer"
        SELLER = "seller", "Seller"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.BUYER)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    @property
    def is_buyer(self):
        return self.role == self.Role.BUYER


class SellerProfile(models.Model):
    """1:1 extension of a User with role=seller.

    seller_type distinguishes the three multi-tenant seller archetypes
    described in the platform spec:
    - 3P: independent/autonomous third-party seller (self-fulfilled).
    - FBP: Fulfilled By Platform — platform manages warehousing/shipping.
    - OEM: manufacturer / OEM-ODM seller producing under platform brands.
    """

    class SellerType(models.TextChoices):
        THIRD_PARTY = "3P", "Third-Party (self-fulfilled)"
        FULFILLED_BY_PLATFORM = "FBP", "Fulfilled by Platform"
        OEM_ODM = "OEM", "Manufacturer OEM/ODM"

    tax_id_validator = RegexValidator(
        regex=r"^[A-Za-z0-9\-]{5,20}$",
        message="tax_id must be 5-20 alphanumeric characters (dashes allowed).",
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="seller_profile"
    )
    company_name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=20, unique=True, validators=[tax_id_validator])
    seller_type = models.CharField(
        max_length=3, choices=SellerType.choices, default=SellerType.THIRD_PARTY
    )
    is_verified = models.BooleanField(default=False)
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        help_text="Platform commission percentage applied to this seller's sales.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "seller_profiles"
        indexes = [models.Index(fields=["seller_type"])]

    def __str__(self):
        return f"{self.company_name} ({self.seller_type})"

    def save(self, *args, **kwargs):
        # Guard against data drift: a SellerProfile must belong to a user
        # with role=seller. We enforce it here rather than only at the
        # serializer layer so direct ORM usage stays consistent too.
        if self.user.role != User.Role.SELLER:
            self.user.role = User.Role.SELLER
            self.user.save(update_fields=["role"])
        super().save(*args, **kwargs)
