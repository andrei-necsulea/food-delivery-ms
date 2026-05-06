#!/usr/bin/env python
"""
Test script: create complete test data for delivery
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
if not driver.phone_number:
    driver.phone_number = '+40742123456'
    driver.vehicle_type = 'motorcycle'
    driver.vehicle_plate = 'DJ-99-TST'
    driver.save()

# Create or get test customer
customer, _ = User.objects.get_or_create(
    username='test_customer',
    defaults={
        'email': 'customer@test.com',
        'role': 'client',
    }
)
if not customer.phone_number:
    customer.phone_number = '+40742654321'
    customer.address = 'Str. Ștefan cel Mare nr 71, Craiova'
    customer.save()

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

# Update order status to OUT_FOR_DELIVERY
order.status = Order.STATUS_OUT_FOR_DELIVERY
order.save()

print("=" * 60)
print("✅ COMPLETE TEST DATA CREATED")
print("=" * 60)
print("\n🏪 RESTAURANT:")
print(f"   Name: {restaurant.name}")
print(f"   Address: {restaurant.address}")
print(f"   Manager: {manager.username}")

print("\n👨 DRIVER:")
print(f"   Username: {driver.username}")
print(f"   Password: test123 (set below)")
print(f"   Email: {driver.email}")
print(f"   Phone: {driver.phone_number}")
print(f"   Vehicle: {driver.vehicle_type} ({driver.vehicle_plate})")

print("\n👩 CUSTOMER:")
print(f"   Username: {customer.username}")
print(f"   Password: test123 (set below)")
print(f"   Email: {customer.email}")
print(f"   Phone: {customer.phone_number}")
print(f"   Address: {customer.address}")

print("\n📦 ORDER:")
print(f"   ID: {order.id}")
print(f"   Status: {order.status}")
print(f"   Total: {order.total_price} lei")
print(f"   Delivery Address: {order.delivery_address}")

print("\n🚚 DELIVERY:")
print(f"   ID: {delivery.id}")
print(f"   Status: {delivery.status}")
print(f"   Current Location: {delivery.location_label}")
print(f"   Coordinates: {delivery.current_latitude}, {delivery.current_longitude}")

print("\n" + "=" * 60)
print("🌐 LINKS:")
print("=" * 60)
print(f"   Route Page: http://127.0.0.1:8000/delivery/route/{order.id}/")
print(f"   Delivery List: http://127.0.0.1:8000/delivery/")
print(f"   Login: http://127.0.0.1:8000/login/")

print("\n" + "=" * 60)
print("✅ CREDENTIALS (use these to login):")
print("=" * 60)
print(f"\n   Driver:")
print(f"   └─ Username: test_driver")
print(f"   └─ Password: test123")
print(f"\n   Customer:")
print(f"   └─ Username: test_customer")
print(f"   └─ Password: test123")
print(f"\n   Admin (if needed):")
print(f"   └─ Access admin at: http://127.0.0.1:8000/admin/")
