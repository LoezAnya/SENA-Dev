from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    """Allows access only to authenticated users with role=seller."""

    message = "Only seller accounts can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_seller
        )


class IsBuyer(BasePermission):
    """Allows access only to authenticated users with role=buyer."""

    message = "Only buyer accounts can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_buyer
        )


class IsOwnerSeller(BasePermission):
    """Object-level permission: only the SellerProfile's own user may edit it."""

    message = "You do not own this seller profile."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
