from decimal import Decimal
import sys

from django.db import transaction

from .models import Category, Product
from . import mongo


_seeded = False


def seed_demo_data():
    global _seeded
    if _seeded:
        return
    try:
        # Avoid seeding during migrate/collectstatic, etc.
        argv = " ".join(sys.argv).lower()
        if any(cmd in argv for cmd in ["makemigrations", "migrate", "collectstatic", "shell", "createsuperuser", "test"]):
            return

        with transaction.atomic():
            cats = {
                "Electronics": None,
                "Fashion": None,
                "Home": None,
                "Books": None,
                "Sports": None,
                "Gaming": None,
            }
            for name in list(cats.keys()):
                cats[name], _ = Category.objects.get_or_create(name=name, defaults={"slug": name.lower()})

            # Baseline items per category
            catalog = {
                "Electronics": [
                    ("Smartphone Pro", "smartphone-pro", "Powerful smartphone with stunning display", Decimal("29999.00")),
                    ("Wireless Earbuds", "wireless-earbuds", "Noise cancelling earbuds", Decimal("4999.00")),
                    ("4K Smart TV", "4k-smart-tv", "Ultra HD LED Smart TV", Decimal("39999.00")),
                ],
                "Fashion": [
                    ("Men's Cotton T-Shirt", "mens-cotton-tshirt", "Comfortable and stylish", Decimal("799.00")),
                    ("Classic Jeans", "classic-jeans", "Slim fit denim", Decimal("1999.00")),
                    ("Women's Summer Dress", "womens-summer-dress", "Light and breezy", Decimal("1499.00")),
                ],
                "Home": [
                    ("Non-stick Cookware Set", "nonstick-cookware", "Durable kitchen set", Decimal("3499.00")),
                    ("Memory Foam Pillow", "memory-foam-pillow", "Orthopedic comfort", Decimal("999.00")),
                    ("Air Purifier", "air-purifier", "HEPA filter for clean air", Decimal("6999.00")),
                ],
                "Books": [
                    ("Bestseller Novel", "bestseller-novel", "Award-winning fiction", Decimal("499.00")),
                    ("Python Crash Course", "python-crash-course", "Practical Python guide", Decimal("899.00")),
                    ("The Pragmatic Programmer", "pragmatic-programmer", "Classic software book", Decimal("1599.00")),
                ],
                "Sports": [
                    ("Football Size 5", "football-size-5", "Match quality ball", Decimal("999.00")),
                    ("Yoga Mat", "yoga-mat", "Non-slip exercise mat", Decimal("799.00")),
                    ("Dumbbell Set 10kg", "dumbbell-set-10kg", "Rubber coated", Decimal("2499.00")),
                ],
                "Gaming": [
                    ("Gaming Mouse RGB", "gaming-mouse-rgb", "High DPI with RGB", Decimal("1499.00")),
                    ("Mechanical Keyboard", "mechanical-keyboard", "Blue switches, RGB", Decimal("3499.00")),
                    ("Gaming Headset 7.1", "gaming-headset-71", "Surround sound", Decimal("2999.00")),
                ],
            }

            ensured = []
            for cat_name, items in catalog.items():
                cat = cats[cat_name]
                # Create or update baseline items by slug
                for title, slug, desc, price in items:
                    p, created = Product.objects.get_or_create(
                        slug=slug,
                        defaults={
                            "title": title,
                            "description": desc,
                            "price": price,
                            "category": cat,
                            "available": True,
                        },
                    )
                    if not created:
                        # ensure fields are up-to-date
                        update_needed = False
                        if p.title != title:
                            p.title = title; update_needed = True
                        if p.description != desc:
                            p.description = desc; update_needed = True
                        if p.price != price:
                            p.price = price; update_needed = True
                        if p.category_id != cat.id:
                            p.category = cat; update_needed = True
                        if not p.available:
                            p.available = True; update_needed = True
                        if update_needed:
                            p.save()
                    ensured.append(p)

            # Mirror to Mongo for fast reads
            for p in ensured:
                try:
                    mongo.upsert_product(p)
                except Exception:
                    pass

        _seeded = True
    except Exception:
        # Never block startup due to seeding
        return
