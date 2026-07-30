from django.urls import include, path
from rest_framework.routers import DefaultRouter

from products.views import (
    ProductImageUploadView,
    PublicProductDetailView,
    PublicProductListView,
    SellerProductVariantViewSet,
    SellerProductViewSet,
)

app_name = "products"

mine_router = DefaultRouter()
mine_router.register("variants", SellerProductVariantViewSet, basename="my-product-variant")
mine_router.register("", SellerProductViewSet, basename="my-product")

urlpatterns = [
    # Public, read-only catalog
    path("", PublicProductListView.as_view(), name="public-list"),
    path("<int:pk>/", PublicProductDetailView.as_view(), name="public-detail"),
    # Seller-only CRUD (own products/variants)
    path("mine/<int:pk>/images/", ProductImageUploadView.as_view(), name="my-product-images"),
    path("mine/", include(mine_router.urls)),
]
