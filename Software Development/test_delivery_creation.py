#!/usr/bin/env python
"""
Test script: create test data for delivery with location_label
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fooddelivery.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from accounts.models import User
from orders.models import Order
from restaurants.models import Restaurant
from delivery.models import Delivery
from menu.models import MenuItem

# Create or get test manager for restaurant
manager, _ = User.objects.get_or_create(
    username='test_manager',
    defaults={
        'email': 'manager@test.com',
        'role': 'manager',
    }
)

# Create or get test restaurant
restaurant, _ = Restaurant.objects.get_or_create(
    name='KFC Electroputere',
    defaults={
        'address': 'Electroputere Mall, Craiova',
        'manager': manager,
    }
)

# Create or get test driver
driver, _ = User.objects.get_or_create(
    username='test_driver',
    defaults={
        'email': 'driver@test.com',
        'role': 'driver',
    }
)

# Create or get test customer
customer, _ = User.objects.get_or_create(
    username='test_customer',
    defaults={
        'email': 'customer@test.com',
        'role': 'client',
    }
)

# Create test menu item
menu_item, _ = MenuItem.objects.get_or_create(
    name='Test Burger',
    restaurant=restaurant,
    defaults={
        'price': 25.00,
        'description': 'Test burger item'
    }
)

# Create test order
order, created = Order.objects.get_or_create(
    id=9999,  # Use fixed ID for testing
    defaults={
        'customer': customer,
        'restaurant': restaurant,
        'status': Order.STATUS_READY,
        'total_price': 50.00,
        'delivery_address': 'Str. Ștefan cel Mare nr 71, Craiova',
    }
)
if not created:
    order.status = Order.STATUS_READY
    order.save()

# Create test delivery with location info
delivery, created = Delivery.objects.get_or_create(
    order=order,
    defaults={
        'driver': driver,
        'status': Delivery.STATUS_ASSIGNED,
        'current_latitude': 44.318300,
        'current_longitude': 23.799000,
        'location_label': 'Str. Ștefan cel Mare nr 71, Craiova',
        'location_code': None,
    }
)

if not created:
    delivery.driver = driver
    delivery.status = Delivery.STATUS_ASSIGNED
    delivery.current_latitude = 44.318300
    delivery.current_longitude = 23.799000
    delivery.location_label = 'Str. Ștefan cel Mare nr 71, Craiova'
    delivery.save()

print("✅ Test data created:")
print(f"   Driver: {driver.username} (ID: {driver.id})")
print(f"   Customer: {customer.username} (ID: {customer.id})")
print(f"   Order: #{order.id} (Status: {order.status})")
print(f"   Delivery: #{delivery.id} (Status: {delivery.status})")
print(f"   Location Label: {delivery.location_label}")
print(f"\n🌐 Access route page at:")
print(f"   http://127.0.0.1:8000/delivery/route/{order.id}/")
print(f"\n👤 Login as driver:")
print(f"   Username: {driver.username}")
print(f"   Password: (whatever password was set)")
