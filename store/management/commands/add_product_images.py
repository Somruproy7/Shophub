import urllib.request
import tempfile
from django.core.management.base import BaseCommand
from store.models import Product
import cloudinary.uploader

class Command(BaseCommand):
    help = 'Upload product images to Cloudinary'

    def handle(self, *args, **options):
        image_urls = {
            'smartphone-pro': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop',
            'wireless-earbuds': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&h=500&fit=crop',
            '4k-smart-tv': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500&h=500&fit=crop',
            'mens-cotton-tshirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&h=500&fit=crop',
            'classic-jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&h=500&fit=crop',
            'womens-summer-dress': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500&h=500&fit=crop',
            'nonstick-cookware': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500&h=500&fit=crop',
            'memory-foam-pillow': 'https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=500&h=500&fit=crop',
            'air-purifier': 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500&h=500&fit=crop',
            'bestseller-novel': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&h=500&fit=crop',
            'python-crash-course': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=500&h=500&fit=crop',
            'pragmatic-programmer': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500&h=500&fit=crop',
            'football-size-5': 'https://images.unsplash.com/photo-1614632537423-1e6c2e7e0aab?w=500&h=500&fit=crop',
            'yoga-mat': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500&h=500&fit=crop',
            'dumbbell-set-10kg': 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=500&h=500&fit=crop',
            'gaming-mouse-rgb': 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=500&h=500&fit=crop',
            'mechanical-keyboard': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&h=500&fit=crop',
            'gaming-headset-71': 'https://images.unsplash.com/photo-1599669454699-248893623440?w=500&h=500&fit=crop',
        }

        for product in Product.objects.all():
            if product.slug in image_urls and not product.image:
                url = image_urls[product.slug]
                try:
                    self.stdout.write(f"Uploading image for {product.title}...")
                    result = cloudinary.uploader.upload(
                        url,
                        public_id=f"products/{product.slug}",
                        overwrite=True,
                    )
                    product.image = result['public_id']
                    product.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ {product.title}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ {product.title}: {e}'))

        self.stdout.write(self.style.SUCCESS('\nDone!'))
