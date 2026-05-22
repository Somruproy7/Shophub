from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Product, Order
from . import mongo
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Exception:
        pass


@receiver(post_save, sender=User)
def sync_user_to_mongo(sender, instance, **kwargs):
    mongo.upsert_user(instance)


@receiver(post_delete, sender=User)
def remove_user_from_mongo(sender, instance, **kwargs):
    mongo.remove_user(instance)


@receiver(post_save, sender=Product)
def sync_product_to_mongo(sender, instance, created, **kwargs):
    image_url = None
    try:
        if instance.image and instance.image.name:
            image_url = instance.image.url
    except Exception as e:
        logger.error(f"Image URL error for {instance.slug}: {e}")
    logger.info(f"Syncing product {instance.slug} to mongo, image_url={image_url}")
    mongo.upsert_product(instance)


@receiver(post_delete, sender=Product)
def remove_product_from_mongo(sender, instance, **kwargs):
    mongo.remove_product(instance)


@receiver(post_save, sender=Order)
def sync_order_to_mongo(sender, instance, created, **kwargs):
    mongo.save_order(instance)
