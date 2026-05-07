from django.test import Client
from django.contrib.auth import get_user_model
from menu.models import MenuItem
from orders.models import Cart, CartItem, Order
from payments.models import Payment
User = get_user_model()
# create online order as test_customer
c = Client()
logged = c.login(username='test_customer', password='test123')
print('customer logged:', logged)
user = User.objects.get(username='test_customer')
mi = MenuItem.objects.filter(restaurant__isnull=False).first()
cart, _ = Cart.objects.get_or_create(customer=user)
cart.restaurant = mi.restaurant
cart.save()
CartItem.objects.filter(cart=cart).delete()
CartItem.objects.create(cart=cart, menu_item=mi, quantity=1)
s = c.session
s['delivery_address'] = 'Str. Stefan cel Mare nr 71, Craiova'
s['phone_number'] = '+40742654321'
s['payment_method'] = 'online'
s.save()
resp = c.post('/orders/checkout/', follow=True)
print('checkout resp', resp.status_code)
order = Order.objects.filter(customer=user).order_by('-created_at').first()
payment = Payment.objects.filter(order=order).first()
print('created order', order.id, 'payment', payment.pk, payment.status)
# Now attempt to accept as manager
manager = order.restaurant.manager
manager.set_password('manager123')
manager.save()
mc = Client()
mlog = mc.login(username=manager.username, password='manager123')
print('manager logged:', mlog, 'user:', manager.username)
# attempt status change
resp2 = mc.post(f'/orders/update/{order.id}/', {'status': Order.STATUS_ACCEPTED}, follow=True)
print('manager accept resp code:', resp2.status_code)
print('resp content len:', len(resp2.content))
# print current payment and order status
order.refresh_from_db()
payment.refresh_from_db()
print('final order status:', order.status, 'payment status:', payment.status)
