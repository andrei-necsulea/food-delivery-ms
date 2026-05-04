from django.db import models
from django.core.validators import MinValueValidator
from restaurants.models import Restaurant


class MenuItem(models.Model):
    CATEGORY_CHOICES = (
        ('burger', 'Burger'),
        ('pizza', 'Pizza'),
        ('pasta', 'Pasta'),
        ('sandwich', 'Sandwich'),
        ('salad', 'Salad'),
        ('soup', 'Soup'),
        ('appetizer', 'Appetizer'),
        ('seafood', 'Seafood'),
        ('grill', 'Grilled Dishes'),
        ('rice', 'Rice & Risotto'),
        ('breakfast', 'Breakfast'),
        ('street_food', 'Street Food'),
        ('snack', 'Snack'),
        ('sides', 'Sides & Dips'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('dessert', 'Dessert'),
        ('drink', 'Drink'),
        ('sauce', 'Sauce'),
        ('traditional', 'Traditional'),
        ('other', 'Other'),
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name