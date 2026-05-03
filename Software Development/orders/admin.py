from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


class CartItemInline(admin.TabularInline):
	model = CartItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'customer', 'restaurant', 'status', 'total_price', 'created_at')
	list_filter = ('status', 'restaurant')
	search_fields = ('customer__username', 'restaurant__name')
	inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ('order', 'menu_item', 'quantity', 'price_at_order_time')
	list_filter = ('order__status',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ('customer', 'restaurant', 'created_at')
	search_fields = ('customer__username', 'restaurant__name')
	inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ('cart', 'menu_item', 'quantity')
