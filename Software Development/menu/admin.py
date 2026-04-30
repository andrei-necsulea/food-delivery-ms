from django.contrib import admin
from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'restaurant', 'price')
	list_filter = ('restaurant',)
	search_fields = ('name', 'description', 'restaurant__name')
