import importlib.util
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fooddelivery.settings')


if importlib.util.find_spec('django') is not None:
    import django

    if not django.apps.apps.ready:
        django.setup()
