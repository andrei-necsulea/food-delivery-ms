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

    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'manager'}
    )

    def __str__(self):
        return self.name


class WorkingHours(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='working_hours'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('restaurant', 'day_of_week')
        ordering = ['day_of_week']

    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK).get(self.day_of_week)
        if self.is_closed:
            return f"{self.restaurant.name} - {day_name}: Closed"
        return f"{self.restaurant.name} - {day_name}: {self.opening_time} - {self.closing_time}"