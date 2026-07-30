from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProductOwner(BasePermission):
    """Allows read to anyone permitted by the view, but restricts
    write operations to the seller who owns the product.
    """

    message = "You do not own this product."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # obj can be a Product or a ProductVariant (via obj.product)
        seller = getattr(obj, "seller", None) or obj.product.seller
        return seller_id_matches(seller, request.user)


def seller_id_matches(seller, user):
    return seller is not None and user is not None and seller.id == user.id
