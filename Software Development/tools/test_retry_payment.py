from django.test import Client
from django.contrib.auth import get_user_model
from menu.models import MenuItem
from orders.models import Cart, CartItem, Order
from payments.models import Payment
User = get_user_model()

# Create online order
c = Client()
logged = c.login(username='test_customer', password='test123')
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
order = Order.objects.filter(customer=user).order_by('-created_at').first()
payment = Payment.objects.filter(order=order).first()
print('Order', order.id, 'Payment', payment.pk, 'Status:', payment.status)

# Admin marks as failed
admin = User.objects.get(username='tmp_admin_pay')
ac = Client()
ac.login(username='tmp_admin_pay', password='adminpay123')
resp = ac.post(f'/payments/{payment.pk}/fail/', {'failure_reason': 'Declined by bank'}, follow=True)
payment.refresh_from_db()
print('After admin fail: status =', payment.status, 'reason =', payment.failure_reason)

# Customer retries
c_retry = Client()
c_retry.login(username='test_customer', password='test123')
resp = c_retry.post(f'/payments/{payment.pk}/retry/', follow=True)
print('Retry resp code:', resp.status_code)
payment.refresh_from_db()
print('After retry: status =', payment.status, 'txn_id =', payment.transaction_id, 'failed_at =', payment.failed_at, 'failure_reason =', payment.failure_reason)
