import django_filters

from products.models import Product


class ProductFilter(django_filters.FilterSet):
    """Backs GET /api/v1/products/?category=&min_price=&max_price=

    `category` accepts either the numeric id or the slug of a
    ProductCategory so the frontend can link from either representation.
    """

    category = django_filters.CharFilter(method="filter_category")
    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price"]

    def filter_category(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(category_id=int(value))
        return queryset.filter(category__slug=value)
