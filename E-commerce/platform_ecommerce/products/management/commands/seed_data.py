"""
Seeds the database with the same demo data as fixtures/*.json, but
using the Django ORM directly (User.objects.create_user, etc.) instead
of a raw JSON fixture. This guarantees passwords are hashed exactly
the way your installed Django version expects, regardless of hasher
configuration.

Usage:
    python manage.py seed_demo_data
    python manage.py seed_demo_data --flush   # wipe seeded data first

Safe to run multiple times: every object is created with get_or_create,
so re-running just confirms/updates rather than duplicating or erroring.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product, ProductCategory, ProductVariant
from users.models import SellerProfile, User

DEMO_PASSWORD = "StrongPass123!"


class Command(BaseCommand):
    help = "Seed the database with demo users, sellers, categories, products and variants."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete previously-seeded demo objects before recreating them.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        categories = self._seed_categories()
        users = self._seed_users()
        self._seed_seller_profiles(users)
        products = self._seed_products(users, categories)
        self._seed_variants(products)

        self.stdout.write(self.style.SUCCESS("\nDemo data ready. Login with any of:"))
        for username in ["buyer1", "buyer2", "seller_3p", "seller_fbp", "seller_oem", "admin_demo"]:
            self.stdout.write(f"  username={username}  password={DEMO_PASSWORD}")

    # -- flush ----------------------------------------------------------
    def _flush(self):
        usernames = ["buyer1", "buyer2", "seller_3p", "seller_fbp", "seller_oem", "admin_demo"]
        ProductVariant.objects.filter(product__seller__username__in=usernames).delete()
        Product.objects.filter(seller__username__in=usernames).delete()
        SellerProfile.objects.filter(user__username__in=usernames).delete()
        User.objects.filter(username__in=usernames).delete()
        ProductCategory.objects.filter(
            slug__in=["tops", "bottoms", "dresses", "shoes", "accessories", "t-shirts", "jeans"]
        ).delete()
        self.stdout.write(self.style.WARNING("Flushed previously-seeded demo data."))

    # -- categories -------------------------------------------------------
    def _seed_categories(self):
        cats = {}
        for name in ["Tops", "Bottoms", "Dresses", "Shoes", "Accessories"]:
            cats[name], _ = ProductCategory.objects.get_or_create(name=name)
        cats["T-Shirts"], _ = ProductCategory.objects.get_or_create(
            name="T-Shirts", defaults={"parent": cats["Tops"]}
        )
        cats["Jeans"], _ = ProductCategory.objects.get_or_create(
            name="Jeans", defaults={"parent": cats["Bottoms"]}
        )
        self.stdout.write(self.style.SUCCESS(f"Categories: {len(cats)} ready."))
        return cats

    # -- users --------------------------------------------------------------
    def _seed_users(self):
        users = {}

        buyer_specs = [
            ("buyer1", "buyer1@example.com", "Ana", "Gomez"),
            ("buyer2", "buyer2@example.com", "Carlos", "Perez"),
        ]
        for username, email, first, last in buyer_specs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "role": User.Role.BUYER,
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save(update_fields=["password"])
            users[username] = user

        seller_specs = [
            ("seller_3p", "seller_3p@example.com", "Laura", "Style Boutique"),
            ("seller_fbp", "seller_fbp@example.com", "Fast", "Fashion Fulfilled"),
            ("seller_oem", "seller_oem@example.com", "Global", "Manufacturing Co"),
        ]
        for username, email, first, last in seller_specs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "role": User.Role.SELLER,
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save(update_fields=["password"])
            users[username] = user

        admin_user, created = User.objects.get_or_create(
            username="admin_demo",
            defaults={
                "email": "admin_demo@example.com",
                "first_name": "Admin",
                "last_name": "Demo",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password(DEMO_PASSWORD)
            admin_user.save(update_fields=["password"])
        users["admin_demo"] = admin_user

        self.stdout.write(self.style.SUCCESS(f"Users: {len(users)} ready."))
        return users

    # -- seller profiles ----------------------------------------------------
    def _seed_seller_profiles(self, users):
        specs = [
            ("seller_3p", "Style Boutique", "TAX-3P-0001", SellerProfile.SellerType.THIRD_PARTY, True, "12.00"),
            ("seller_fbp", "Fast Fashion Fulfilled", "TAX-FBP-0002", SellerProfile.SellerType.FULFILLED_BY_PLATFORM, True, "8.50"),
            ("seller_oem", "Global Manufacturing Co", "TAX-OEM-0003", SellerProfile.SellerType.OEM_ODM, False, "5.00"),
        ]
        for username, company, tax_id, seller_type, verified, commission in specs:
            SellerProfile.objects.get_or_create(
                user=users[username],
                defaults={
                    "company_name": company,
                    "tax_id": tax_id,
                    "seller_type": seller_type,
                    "is_verified": verified,
                    "commission_rate": Decimal(commission),
                },
            )
        self.stdout.write(self.style.SUCCESS("Seller profiles ready."))

    # -- products -------------------------------------------------------------
    def _seed_products(self, users, cats):
        specs = [
            ("seller_3p", "Tops", "Blusa Floral Manga Larga",
             "Blusa ligera con estampado floral, ideal para primavera.", "18.99", 120,
             ["https://picsum.photos/id/1011/1340/1785"], True),
            ("seller_fbp", "T-Shirts", "Camiseta Basica Algodon",
             "Camiseta 100% algodon, corte unisex, varios colores.", "9.99", 300,
             ["https://picsum.photos/id/1025/1340/1785"], True),
            ("seller_3p", "Dresses", "Vestido Midi Verano",
             "Vestido midi de tirantes, tela fresca, perfecto para el dia a dia.", "34.50", 60,
             ["https://picsum.photos/id/1027/1340/1785"], True),
            ("seller_fbp", "Jeans", "Jeans Skinny Tiro Alto",
             "Jeans skinny de tiro alto con efecto push-up.", "27.90", 85,
             ["https://picsum.photos/id/1035/1340/1785"], True),
            ("seller_3p", "Bottoms", "Falda Plisada",
             "Falda plisada midi, cintura elastica.", "22.00", 45, [], True),
            ("seller_oem", "Shoes", "Tenis Urbanos Blancos",
             "Tenis urbanos unisex, suela antideslizante.", "45.00", 40,
             ["https://picsum.photos/id/103/1340/1785"], True),
            ("seller_3p", "Shoes", "Sandalias Plataforma",
             "Sandalias de plataforma con tiras ajustables.", "31.75", 25,
             ["https://picsum.photos/id/104/1340/1785"], True),
            ("seller_fbp", "Accessories", "Bolso Tote Cuero Sintetico",
             "Bolso tote espacioso, cuero sintetico de alta durabilidad.", "39.90", 30,
             ["https://picsum.photos/id/1060/1340/1785"], True),
            ("seller_oem", "Accessories", "Gafas de Sol Ovaladas",
             "Gafas de sol con proteccion UV400, montura ovalada.", "12.50", 150, [], True),
            ("seller_oem", "Tops", "Chaqueta Denim Oversize",
             "Chaqueta de mezclilla oversize, descontinuada temporada pasada.", "42.00", 0,
             ["https://picsum.photos/id/1074/1340/1785"], False),
        ]
        products = {}
        for seller_username, cat_name, name, desc, price, stock, images, active in specs:
            product, _ = Product.objects.get_or_create(
                seller=users[seller_username],
                name=name,
                defaults={
                    "category": cats[cat_name],
                    "description": desc,
                    "base_price": Decimal(price),
                    "stock": stock,
                    "images": images,
                    "is_active": active,
                },
            )
            products[name] = product
        self.stdout.write(self.style.SUCCESS(f"Products: {len(products)} ready."))
        return products

    # -- variants ---------------------------------------------------------
    def _seed_variants(self, products):
        specs = [
            ("Camiseta Basica Algodon", "Black", "S", "TEE-BLK-S", 50, None),
            ("Camiseta Basica Algodon", "Black", "M", "TEE-BLK-M", 80, None),
            ("Camiseta Basica Algodon", "White", "M", "TEE-WHT-M", 70, "8.99"),
            ("Jeans Skinny Tiro Alto", "Blue", "26", "JEAN-BLU-26", 20, None),
            ("Jeans Skinny Tiro Alto", "Blue", "28", "JEAN-BLU-28", 35, None),
            ("Tenis Urbanos Blancos", "White", "39", "SNKR-WHT-39", 15, None),
            ("Tenis Urbanos Blancos", "White", "40", "SNKR-WHT-40", 12, "49.00"),
        ]
        count = 0
        for product_name, color, size, sku, stock, price_override in specs:
            _, created = ProductVariant.objects.get_or_create(
                product=products[product_name],
                color=color,
                size=size,
                defaults={
                    "sku": sku,
                    "stock": stock,
                    "price_override": Decimal(price_override) if price_override else None,
                },
            )
            count += created
        self.stdout.write(self.style.SUCCESS("Variants ready."))
