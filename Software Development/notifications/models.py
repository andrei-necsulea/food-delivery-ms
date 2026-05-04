
from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
from delivery.models import Delivery

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPE_ORDER = 'order'
    NOTIFICATION_TYPE_DELIVERY = 'delivery'
    NOTIFICATION_TYPE_SYSTEM = 'system'

    NOTIFICATION_TYPES = (
        (NOTIFICATION_TYPE_ORDER, 'Order'),
        (NOTIFICATION_TYPE_DELIVERY, 'Delivery'),
        (NOTIFICATION_TYPE_SYSTEM, 'System'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default=NOTIFICATION_TYPE_SYSTEM)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

    @classmethod
    def create_order_notification(cls, user, order, title, message):
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=cls.NOTIFICATION_TYPE_ORDER,
            order=order
        )

    @classmethod
    def create_delivery_notification(cls, user, delivery, title, message):
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=cls.NOTIFICATION_TYPE_DELIVERY,
            delivery=delivery
        )

    @classmethod
    def create_system_notification(cls, user, title, message):
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=cls.NOTIFICATION_TYPE_SYSTEM
        )
