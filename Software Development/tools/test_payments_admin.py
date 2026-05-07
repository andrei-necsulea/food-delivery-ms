from django.test import Client
from django.contrib.auth import get_user_model
from payments.models import Payment
User = get_user_model()
user = User.objects.get(username='test_customer')
qs = list(Payment.objects.filter(order__customer=user).order_by('-created_at'))
print('payments pks:', [(p.pk,p.order.id,p.method,p.status) for p in qs])
if not qs:
    print('no payments')
    exit(0)
online = qs[0]
cash = qs[-1] if len(qs)>1 else qs[0]
admin, created = User.objects.get_or_create(username='tmp_admin_pay', defaults={'role':'admin','is_staff':True,'is_superuser':True,'email':'tmp_admin_pay@example.com'})
if created:
    admin.set_password('adminpay123')
    admin.save()
c = Client()
logged = c.login(username='tmp_admin_pay', password='adminpay123')
print('admin logged:', logged)
resp = c.post(f'/payments/{online.pk}/confirm/', follow=True)
print('confirm resp', resp.status_code)
online.refresh_from_db()
print('online now:', online.status, online.paid_at)
resp2 = c.post(f'/payments/{cash.pk}/fail/', {'failure_reason':'declined'}, follow=True)
print('fail resp', resp2.status_code)
cash.refresh_from_db()
print('cash now:', cash.status, cash.failed_at, cash.failure_reason)
