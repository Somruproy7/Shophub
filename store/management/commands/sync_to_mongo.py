from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from store.models import Product, Order
from store import mongo

class Command(BaseCommand):
    help = 'Sync products, orders, and users from Django DB to MongoDB'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting sync to MongoDB...'))
        
        # Sync users
        self.stdout.write('\nSyncing users...')
        user_count = 0
        for u in User.objects.all():
            try:
                mongo.upsert_user(u)
                user_count += 1
                role = 'Admin' if u.is_superuser else 'Staff' if u.is_staff else 'User'
                self.stdout.write(f'  ✓ Synced: {u.username} ({role})')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to sync {u.username}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Users synced: {user_count}'))
        
        # Sync products
        self.stdout.write('\nSyncing products...')
        product_count = 0
        for p in Product.objects.all():
            try:
                mongo.upsert_product(p)
                product_count += 1
                self.stdout.write(f'  ✓ Synced: {p.title}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to sync {p.title}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Products synced: {product_count}'))

        # Sync orders
        self.stdout.write('\nSyncing orders...')
        order_count = 0
        for o in Order.objects.all():
            try:
                mongo.save_order(o)
                order_count += 1
                self.stdout.write(f'  ✓ Synced: Order #{o.id}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to sync Order #{o.id}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Orders synced: {order_count}'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS(f'✓ Sync completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  Users: {user_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Products: {product_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Orders: {order_count}'))
        self.stdout.write(self.style.SUCCESS('='*50))
