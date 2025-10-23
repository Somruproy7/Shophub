from django.core.management.base import BaseCommand

from store.models import Product, Order
from store import mongo

class Command(BaseCommand):
    help = 'Sync products and orders from Django DB to MongoDB'

    def handle(self, *args, **options):
        self.stdout.write('Syncing products...')
        for p in Product.objects.all():
            mongo.upsert_product(p)
        self.stdout.write('Products synced.')

        self.stdout.write('Syncing orders...')
        for o in Order.objects.all():
            mongo.save_order(o)
        self.stdout.write('Orders synced.')
