from django.db import models
from accounts.models import User


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    description = models.TextField(blank=True)
    cuisine_type = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    delivery_time = models.CharField(max_length=50, default="30-45 min")
    working_hours = models.CharField(max_length=100, default="10:00 - 22:00")

    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'manager'}
    )

    def __str__(self):
        return self.name