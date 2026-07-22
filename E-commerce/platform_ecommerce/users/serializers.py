from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers

from users.models import SellerProfile, User


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = [
            "id",
            "company_name",
            "tax_id",
            "seller_type",
            "is_verified",
            "commission_rate",
            "created_at",
        ]
        read_only_fields = ["id", "is_verified", "commission_rate", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    """Read-facing representation of a user, used for the /me endpoint."""

    seller_profile = SellerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "phone_number",
            "seller_profile",
            "date_joined",
        ]
        read_only_fields = ["id", "role", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    """Handles registration for both buyer and seller roles.

    When role == "seller", the caller must also supply company_name,
    tax_id and seller_type, which are used to create the linked
    SellerProfile in the same transaction.
    """

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[User.Role.BUYER, User.Role.SELLER], default=User.Role.BUYER
    )

    # Seller-only fields (optional, required only when role == seller)
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tax_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    seller_type = serializers.ChoiceField(
        choices=SellerProfile.SellerType.choices, required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "role",
            "phone_number",
            "company_name",
            "tax_id",
            "seller_type",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        password_validation.validate_password(attrs["password"])

        if attrs.get("role") == User.Role.SELLER:
            missing = [
                field
                for field in ("company_name", "tax_id", "seller_type")
                if not attrs.get(field)
            ]
            if missing:
                raise serializers.ValidationError(
                    {
                        field: "This field is required when role=seller."
                        for field in missing
                    }
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password_confirm")
        company_name = validated_data.pop("company_name", None)
        tax_id = validated_data.pop("tax_id", None)
        seller_type = validated_data.pop("seller_type", None)
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)

        if user.role == User.Role.SELLER:
            SellerProfile.objects.create(
                user=user,
                company_name=company_name,
                tax_id=tax_id,
                seller_type=seller_type,
            )
        return user
