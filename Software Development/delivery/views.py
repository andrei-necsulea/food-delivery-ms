from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Delivery
from orders.models import Order
from accounts.models import User
from accounts.decorators import role_required


@role_required(['admin', 'driver'])
def delivery_list(request):
    if request.user.role == 'admin':
        deliveries = Delivery.objects.select_related(
            'order', 'order__customer', 'order__restaurant', 'driver'
        ).all()
    else:
        deliveries = Delivery.objects.select_related(
            'order', 'order__customer', 'order__restaurant', 'driver'
        ).filter(driver=request.user)

    return render(request, 'delivery/delivery_list.html', {'deliveries': deliveries})


@role_required(['admin'])
def delivery_create(request):
    deliveries_with_order_ids = Delivery.objects.values_list('order_id', flat=True)
    orders = Order.objects.exclude(id__in=deliveries_with_order_ids).filter(
        status=Order.STATUS_OUT_FOR_DELIVERY
    )
    drivers = User.objects.filter(role='driver')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        driver_id = request.POST.get('driver_id')
        status = request.POST.get('status')

        delivery = Delivery.objects.create(
            order_id=order_id,
            driver_id=driver_id if driver_id else None,
            status=status
        )

        if delivery.status in [Delivery.STATUS_ASSIGNED, Delivery.STATUS_PICKED_UP, Delivery.STATUS_ON_THE_WAY]:
            delivery.order.status = Order.STATUS_OUT_FOR_DELIVERY
            delivery.order.save()

        if delivery.status == Delivery.STATUS_DELIVERED:
            delivery.order.status = Order.STATUS_DELIVERED
            delivery.order.save()

        messages.success(request, 'Delivery created successfully.')
        return redirect('delivery_list')

    return render(request, 'delivery/delivery_form.html', {
        'orders': orders,
        'drivers': drivers,
        'driver_mode': False,
        'allowed_statuses': [choice[0] for choice in Delivery.STATUS_CHOICES],
    })


@role_required(['admin', 'driver'])
def delivery_update(request, pk):
    if request.user.role == 'admin':
        delivery = get_object_or_404(Delivery, pk=pk)
        deliveries_with_order_ids = Delivery.objects.exclude(pk=pk).values_list('order_id', flat=True)
        orders = Order.objects.exclude(id__in=deliveries_with_order_ids)
        drivers = User.objects.filter(role='driver')

        if request.method == 'POST':
            delivery.order_id = request.POST.get('order_id')
            driver_id = request.POST.get('driver_id')
            delivery.driver_id = driver_id if driver_id else None
            delivery.status = request.POST.get('status')
            delivery.save()

            if delivery.status in [Delivery.STATUS_ASSIGNED, Delivery.STATUS_PICKED_UP, Delivery.STATUS_ON_THE_WAY]:
                delivery.order.status = Order.STATUS_OUT_FOR_DELIVERY
                delivery.order.save()

            if delivery.status == Delivery.STATUS_DELIVERED:
                delivery.order.status = Order.STATUS_DELIVERED
                delivery.order.save()

            messages.success(request, 'Delivery updated successfully.')
            return redirect('delivery_list')

        return render(request, 'delivery/delivery_form.html', {
            'delivery': delivery,
            'orders': orders,
            'drivers': drivers,
            'driver_mode': False,
            'allowed_statuses': [choice[0] for choice in Delivery.STATUS_CHOICES],
        })

    delivery = get_object_or_404(Delivery, pk=pk, driver=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed_statuses = delivery.get_allowed_next_statuses_for_driver()

        if new_status not in allowed_statuses:
            messages.error(request, 'Invalid delivery status transition.')
            return HttpResponseForbidden("Invalid delivery status transition.")

        delivery.status = new_status
        delivery.save()

        if delivery.status in [Delivery.STATUS_PICKED_UP, Delivery.STATUS_ON_THE_WAY]:
            delivery.order.status = Order.STATUS_OUT_FOR_DELIVERY
            delivery.order.save()

        if delivery.status == Delivery.STATUS_DELIVERED:
            delivery.order.status = Order.STATUS_DELIVERED
            delivery.order.save()

        messages.success(request, 'Delivery status updated successfully.')
        return redirect('delivery_list')

    return render(request, 'delivery/delivery_form.html', {
        'delivery': delivery,
        'driver_mode': True,
        'allowed_statuses': delivery.get_allowed_next_statuses_for_driver(),
    })


@role_required(['admin'])
def delivery_delete(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)

    if request.method == 'POST':
        delivery.delete()
        messages.success(request, 'Delivery deleted successfully.')
        return redirect('delivery_list')

    return render(request, 'delivery/delivery_confirm_delete.html', {'delivery': delivery})