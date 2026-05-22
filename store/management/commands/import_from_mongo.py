from django.core.management.base import BaseCommand
from store import mongo
from store.models import Product, Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Import products from MongoDB into PostgreSQL'

    def handle(self, *args, **options):
        products = mongo.get_db().products.find()
        count = 0
        skipped = 0

        for doc in products:
            title = doc.get('title', '')
            slug = doc.get('slug') or slugify(title)
            price = doc.get('price', 0)
            description = doc.get('description', '')
            available = doc.get('available', True)
            category_name = doc.get('category')

            if not title or not slug:
                skipped += 1
                continue

            # Get or create category
            category = None
            if category_name:
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'slug': slugify(category_name)}
                )

            # Skip if product with this slug already exists
            if Product.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Skipping existing: {title}')
                skipped += 1
                continue

            # Create product (no image — needs to be uploaded manually)
            Product.objects.create(
                title=title,
                slug=slug,
                description=description,
                price=price,
                available=available,
                category=category,
            )
            count += 1
            self.stdout.write(f'  Imported: {title}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Imported {count} products, skipped {skipped}.'
        ))
        self.stdout.write(
            'Note: Product images need to be uploaded manually via admin.'
        )