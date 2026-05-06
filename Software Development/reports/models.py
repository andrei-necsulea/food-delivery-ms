
from django.db import models
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from delivery.models import Delivery
from restaurants.models import Restaurant
from accounts.models import User


class DailyAggregation(models.Model):
    """Store daily aggregated statistics for performance"""
    date = models.DateField(unique=True)
    total_orders = models.IntegerField(default=0)
    completed_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_delivery_time = models.FloatField(default=0)  # in minutes
    active_drivers = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Daily Aggregation'
        verbose_name_plural = 'Daily Aggregations'
        ordering = ['-date']

    def __str__(self):
        return f"Aggregation for {self.date}"


class RestaurantMetrics(models.Model):
    """Store restaurant performance metrics"""
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='metrics')
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_order_value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    avg_rating = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Restaurant Metrics'
        verbose_name_plural = 'Restaurant Metrics'

    def __str__(self):
        return f"{self.restaurant.name} - Metrics"


class DriverMetrics(models.Model):
    """Store driver performance metrics"""
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metrics', limit_choices_to={'role': 'driver'})
    total_deliveries = models.IntegerField(default=0)
    completed_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    avg_delivery_time = models.FloatField(default=0)  # in minutes
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_rating = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Driver Metrics'
        verbose_name_plural = 'Driver Metrics'

    def __str__(self):
        return f"{self.driver.username} - Metrics"

