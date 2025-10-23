from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_delete
from .models import Product, Order
from . import mongo


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


# Sync products to MongoDB
@receiver(post_save, sender=Product)
def sync_product_to_mongo(sender, instance, created, **kwargs):
    mongo.upsert_product(instance)


@receiver(post_delete, sender=Product)
def remove_product_from_mongo(sender, instance, **kwargs):
    mongo.remove_product(instance)


# When an order is saved, persist it to MongoDB
@receiver(post_save, sender=Order)
def sync_order_to_mongo(sender, instance, created, **kwargs):
    # always upsert order doc
    mongo.save_order(instance)
