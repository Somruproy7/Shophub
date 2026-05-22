from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    def ready(self):
        try:
            import store.signals  # noqa: F401
        except Exception:
            pass
        try:
            from . import seed
            seed.seed_demo_data()
        except Exception:
            pass
