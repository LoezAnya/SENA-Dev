"""platform_ecommerce URL configuration — Sprint 1."""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth / users app owns registration, login and profile endpoints.
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Reserved for Sprint 2+ (catalog, orders) — apps exist but expose
    # no routes yet in this sprint.
    # path("api/v1/products/", include("products.urls")),
    # path("api/v1/orders/", include("orders.urls")),
]
