from django.db import models
from orders.models import Order
from accounts.models import User


class Delivery(models.Model):
    STATUS_ASSIGNED = 'assigned'
    STATUS_PICKED_UP = 'picked_up'
    STATUS_ON_THE_WAY = 'on_the_way'
    STATUS_DELIVERED = 'delivered'

    STATUS_CHOICES = (
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_PICKED_UP, 'Picked Up'),
        (STATUS_ON_THE_WAY, 'On The Way'),
        (STATUS_DELIVERED, 'Delivered'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'driver'},
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ASSIGNED
    )
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery #{self.id} - Order {self.order.id}"

    def get_allowed_next_statuses_for_driver(self):
        transitions = {
            self.STATUS_ASSIGNED: [self.STATUS_PICKED_UP],
            self.STATUS_PICKED_UP: [self.STATUS_ON_THE_WAY],
            self.STATUS_ON_THE_WAY: [self.STATUS_DELIVERED],
            self.STATUS_DELIVERED: [],
        }
        return transitions.get(self.status, [])