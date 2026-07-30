"""
Load test for the public product catalog (Sprint 2 acceptance criterion:
p95 response time < 500ms on local/dev environment).

Run against a live server with:
    locust -f products/locustfile.py --host=http://localhost:8000

Then open http://localhost:8089 to configure users/spawn-rate and start
the run, or run headless, e.g.:
    locust -f products/locustfile.py --host=http://localhost:8000 \
        --users 50 --spawn-rate 5 --run-time 2m --headless \
        --csv=sprint2_load_test
"""
import random

from locust import HttpUser, between, task

CATEGORIES = ["tops", "bottoms", "shoes", "accessories", "dresses"]


class CatalogBrowser(HttpUser):
    """Simulates a buyer browsing the public catalog: list, filter,
    search, paginate, and view product detail — the read-heavy traffic
    pattern the Sprint 2 cache layer is meant to absorb.
    """

    wait_time = between(1, 3)

    @task(5)
    def browse_catalog(self):
        self.client.get("/api/v1/products/", name="/products/ (list)")

    @task(3)
    def filter_by_category(self):
        category = random.choice(CATEGORIES)
        self.client.get(
            f"/api/v1/products/?category={category}",
            name="/products/?category=... (filter)",
        )

    @task(2)
    def filter_by_price_range(self):
        min_price = random.choice([0, 10, 20])
        max_price = min_price + random.choice([20, 50, 100])
        self.client.get(
            f"/api/v1/products/?min_price={min_price}&max_price={max_price}",
            name="/products/?min_price=&max_price= (filter)",
        )

    @task(2)
    def search_products(self):
        term = random.choice(["dress", "shirt", "jean", "shoe", "bag"])
        self.client.get(
            f"/api/v1/products/?search={term}", name="/products/?search=... (search)"
        )

    @task(1)
    def paginate(self):
        page = random.randint(1, 5)
        self.client.get(f"/api/v1/products/?page={page}", name="/products/?page=N")

    @task(2)
    def view_detail(self):
        product_id = random.randint(1, 50)
        self.client.get(
            f"/api/v1/products/{product_id}/", name="/products/{id}/ (detail)"
        )
