from django.contrib import admin
from .models import Restaurant, WorkingHours


class WorkingHoursInline(admin.TabularInline):
	model = WorkingHours
	extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
	list_display = ('name', 'manager', 'cuisine_type', 'rating', 'delivery_time')
	list_filter = ('cuisine_type', 'manager')
	search_fields = ('name', 'address', 'cuisine_type')
	inlines = [WorkingHoursInline]


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
	list_display = ('restaurant', 'day_of_week', 'opening_time', 'closing_time', 'is_closed')
	list_filter = ('restaurant', 'day_of_week', 'is_closed')
