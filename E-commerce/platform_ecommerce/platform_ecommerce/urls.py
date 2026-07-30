"""platform_ecommerce URL configuration — Sprint 2."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth / users app owns registration, login and profile endpoints.
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Catalog (public listing/detail + seller CRUD under /mine/).
    path("api/v1/products/", include("products.urls")),
    # Reserved for Sprint 3+ (orders/payments) — app exists but exposes
    # no routes yet.
    # path("api/v1/orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
