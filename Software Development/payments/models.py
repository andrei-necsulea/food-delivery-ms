from django.db import models
from orders.models import Order


class Payment(models.Model):
    METHOD_CASH_ON_DELIVERY = 'cash'
    METHOD_ONLINE = 'online'

    METHOD_CHOICES = (
        (METHOD_CASH_ON_DELIVERY, 'Cash on Delivery'),
        (METHOD_ONLINE, 'Online Payment'),
    )

    STATUS_UNPAID = 'unpaid'
    STATUS_PENDING_PAYMENT = 'pending_payment'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = (
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_PENDING_PAYMENT, 'Pending Payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_UNPAID)
    transaction_id = models.CharField(max_length=120, blank=True, null=True, unique=True)
    provider_reference = models.CharField(max_length=120, blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    failed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment for order {self.order_id} ({self.status})"