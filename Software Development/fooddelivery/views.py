from django.shortcuts import render
from accounts.decorators import role_required
from restaurants.models import Restaurant
from menu.models import MenuItem
from orders.models import Order
from delivery.models import Delivery


def home(request):
    context = {}

    if request.user.is_authenticated:
        role = request.user.role
        context['role'] = role

        if role == 'admin':
            context['total_restaurants'] = Restaurant.objects.count()
            context['total_menu_items'] = MenuItem.objects.count()
            context['total_orders'] = Order.objects.count()
            context['total_deliveries'] = Delivery.objects.count()

            context['created_orders'] = Order.objects.filter(status=Order.STATUS_CREATED).count()
            context['delivered_orders'] = Order.objects.filter(status=Order.STATUS_DELIVERED).count()

        elif role == 'manager':
            my_restaurants = Restaurant.objects.filter(manager=request.user)
            my_orders = Order.objects.filter(restaurant__manager=request.user)
            my_menu_items = MenuItem.objects.filter(restaurant__manager=request.user)

            context['my_restaurants_count'] = my_restaurants.count()
            context['my_menu_items_count'] = my_menu_items.count()
            context['my_orders_count'] = my_orders.count()
            context['my_active_orders_count'] = my_orders.exclude(
                status__in=[Order.STATUS_DELIVERED, Order.STATUS_CANCELLED]
            ).count()

        elif role == 'client':
            my_orders = Order.objects.filter(customer=request.user)

            context['my_orders_count'] = my_orders.count()
            context['my_active_orders_count'] = my_orders.exclude(
                status__in=[Order.STATUS_DELIVERED, Order.STATUS_CANCELLED]
            ).count()
            context['my_delivered_orders_count'] = my_orders.filter(
                status=Order.STATUS_DELIVERED
            ).count()
            context['my_cancelled_orders_count'] = my_orders.filter(
                status=Order.STATUS_CANCELLED
            ).count()

        elif role == 'driver':
            my_deliveries = Delivery.objects.filter(driver=request.user)

            context['my_deliveries_count'] = my_deliveries.count()
            context['my_delivered_count'] = my_deliveries.filter(
                status=Delivery.STATUS_DELIVERED
            ).count()
            context['my_in_progress_count'] = my_deliveries.exclude(
                status=Delivery.STATUS_DELIVERED
            ).count()

    return render(request, 'home.html', context)


@role_required(['manager'])
def manager_panel(request):
    my_restaurants = Restaurant.objects.filter(manager=request.user)
    my_orders = Order.objects.filter(restaurant__manager=request.user).select_related('customer', 'restaurant')
    my_menu_items = MenuItem.objects.filter(restaurant__manager=request.user).select_related('restaurant')

    context = {
        'my_restaurants': my_restaurants,
        'my_orders': my_orders[:10],
        'my_menu_items': my_menu_items,
        'my_restaurants_count': my_restaurants.count(),
        'my_menu_items_count': my_menu_items.count(),
        'my_orders_count': my_orders.count(),
        'my_active_orders_count': my_orders.exclude(
            status__in=[Order.STATUS_DELIVERED, Order.STATUS_CANCELLED]
        ).count(),
        'working_hours_edit_base': 'working_hours_edit',
    }
    return render(request, 'manager_panel.html', context)