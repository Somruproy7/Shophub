from pymongo import MongoClient
from django.conf import settings
from datetime import datetime

_client = None


def get_client():
    global _client
    if _client is None:
        uri = getattr(settings, 'MONGO_URI', None) or 'mongodb://localhost:27017'
        _client = MongoClient(uri)
    return _client


def get_db():
    client = get_client()
    dbname = getattr(settings, 'MONGO_DB_NAME', None) or getattr(settings, 'MONGO_DB_NAME', 'myecommerce_db')
    return client[dbname]


def upsert_product(product):
    """Upsert a Product instance into MongoDB products collection."""
    try:
        db = get_db()
        doc = {
            '_id': int(product.id),
            'title': product.title,
            'slug': product.slug,
            'description': product.description,
            'price': float(product.price),
            'available': bool(product.available),
            'created_at': product.created_at.isoformat() if getattr(product, 'created_at', None) else datetime.utcnow().isoformat(),
            'category': product.category.name if getattr(product, 'category', None) else None,
            'image_url': product.image.url if getattr(product, 'image', None) and getattr(product.image, 'url', None) else None,
        }
        db.products.replace_one({'_id': doc['_id']}, doc, upsert=True)
    except Exception:
        # Fail silently to avoid breaking the main request flow
        pass


def remove_product(product):
    try:
        db = get_db()
        db.products.delete_one({'_id': int(product.id)})
    except Exception:
        pass


def get_products(limit=50, q=None, category=None):
    try:
        db = get_db()
        filt = {'available': True}
        if category:
            filt['category'] = category
        if q:
            # case-insensitive regex search on title/description
            filt['$or'] = [
                {'title': {'$regex': q, '$options': 'i'}},
                {'description': {'$regex': q, '$options': 'i'}},
            ]
        cursor = db.products.find(filt).sort('created_at', -1)
        # Only apply limit when it's a positive integer; limit(0) or None means no limit
        if isinstance(limit, int) and limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
    except Exception:
        return []


def get_product_by_slug(slug):
    try:
        db = get_db()
        return db.products.find_one({'slug': slug})
    except Exception:
        return None


def save_order(order):
    """Save Order and its items to MongoDB orders collection."""
    try:
        db = get_db()
        items = []
        for it in order.items.all():
            items.append({
                'product_id': int(it.product.id) if it.product else None,
                'title': it.product.title if it.product else None,
                'quantity': int(it.quantity),
                'price': float(it.price),
            })

        doc = {
            '_id': int(order.id),
            'user_id': int(order.user.id) if order.user else None,
            'username': order.user.username if order.user else None,
            'address': {
                'full_name': order.address.full_name if order.address else None,
                'line1': order.address.line1 if order.address else None,
                'city': order.address.city if order.address else None,
                'postal_code': order.address.postal_code if order.address else None,
                'country': order.address.country if order.address else None,
            },
            'items': items,
            'total': float(order.total),
            'payment_method': order.payment_method,
            'paid': bool(order.paid),
            'created_at': order.created_at.isoformat() if getattr(order, 'created_at', None) else datetime.utcnow().isoformat(),
        }
        db.orders.replace_one({'_id': doc['_id']}, doc, upsert=True)
    except Exception:
        pass


def upsert_user(user):
    """Upsert a User instance into MongoDB users collection."""
    try:
        db = get_db()
        doc = {
            '_id': int(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': bool(user.is_staff),
            'is_superuser': bool(user.is_superuser),
            'is_active': bool(user.is_active),
            'date_joined': user.date_joined.isoformat() if getattr(user, 'date_joined', None) else datetime.utcnow().isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
        
        # Add profile info if exists
        if hasattr(user, 'profile'):
            profile = user.profile
            doc['profile'] = {
                'phone': getattr(profile, 'phone', None),
                'avatar_url': profile.avatar.url if getattr(profile, 'avatar', None) and getattr(profile.avatar, 'url', None) else None,
            }
        
        db.users.replace_one({'_id': doc['_id']}, doc, upsert=True)
    except Exception:
        pass


def remove_user(user):
    """Remove a user from MongoDB users collection."""
    try:
        db = get_db()
        db.users.delete_one({'_id': int(user.id)})
    except Exception:
        pass


def get_users(limit=50):
    """Get all users from MongoDB."""
    try:
        db = get_db()
        cursor = db.users.find().sort('date_joined', -1)
        if isinstance(limit, int) and limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
    except Exception:
        return []
