
from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'method', 'status', 'transaction_id', 'created_at', 'updated_at')
	list_filter = ('method', 'status', 'created_at')
	search_fields = ('order__id', 'transaction_id', 'provider_reference')
