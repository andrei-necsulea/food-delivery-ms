from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from .models import Delivery
from orders.models import Order
from accounts.models import User
from accounts.decorators import role_required
from notifications.models import Notification


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


@role_required(['driver'])
def available_orders(request):
    assigned_order_ids = Delivery.objects.values_list('order_id', flat=True)
    orders = Order.objects.exclude(id__in=assigned_order_ids).filter(
        status__in=[Order.STATUS_ACCEPTED, Order.STATUS_PREPARING, Order.STATUS_READY]
    ).select_related('customer', 'restaurant')

    return render(request, 'delivery/available_orders.html', {
        'orders': orders,
    })


@role_required(['driver'])
def take_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status__in=[Order.STATUS_ACCEPTED, Order.STATUS_PREPARING, Order.STATUS_READY])
    if Delivery.objects.filter(order=order).exists():
        messages.error(request, 'This order has already been taken by another driver.')
        return redirect('available_orders')

    if request.method == 'POST':
        delivery = Delivery.objects.create(
            order=order,
            driver=request.user,
            status=Delivery.STATUS_ASSIGNED
        )
        order.status = Order.STATUS_OUT_FOR_DELIVERY
        order.save()

        Notification.create_delivery_notification(
            user=order.customer,
            delivery=delivery,
            title='Delivery Assigned',
            message=f'Your order #{order.id} has been assigned to courier {request.user.username}.'
        )

        messages.success(request, f'Order #{order.id} has been assigned to you.')
        return redirect('delivery_list')

    return render(request, 'delivery/take_order_confirm.html', {
        'order': order,
    })


@role_required(['admin', 'driver', 'client'])
def route_info(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.user.role == 'client' and order.customer != request.user:
        return HttpResponseForbidden('You are not allowed to view this route information.')

    delivery = Delivery.objects.filter(order=order).first()

    if request.method == 'POST':
        if request.user.role != 'driver' or not delivery or delivery.driver != request.user:
            return HttpResponseForbidden('You are not allowed to update this route information.')

        latitude = request.POST.get('current_latitude')
        longitude = request.POST.get('current_longitude')

        if latitude and longitude:
            try:
                delivery.current_latitude = float(latitude)
                delivery.current_longitude = float(longitude)
                delivery.save()
                messages.success(request, 'Courier location updated successfully.')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid coordinates provided. Please try again.')
        else:
            messages.error(request, 'Location update failed. Please allow browser location access or enter coordinates manually.')

        return redirect('route_info', order_id=order.id)

    return render(request, 'delivery/route_info.html', {
        'order': order,
        'delivery': delivery,
    })


@role_required(['admin', 'driver', 'client'])
def route_data(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.user.role == 'client' and order.customer != request.user:
        return HttpResponseForbidden('You are not allowed to view this route information.')

    delivery = Delivery.objects.filter(order=order).first()
    if not delivery:
        return JsonResponse({'error': 'No delivery record found.'}, status=404)

    return JsonResponse({
        'order_id': order.id,
        'delivery_id': delivery.id,
        'status': delivery.status,
        'current_latitude': delivery.current_latitude,
        'current_longitude': delivery.current_longitude,
        'driver': {
            'id': delivery.driver.id if delivery.driver else None,
            'username': delivery.driver.username if delivery.driver else None,
        }
    })


@role_required(['driver'])
def update_courier_location(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id, driver=request.user)

    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not latitude or not longitude:
            return JsonResponse({'error': 'Latitude and longitude are required.'}, status=400)

        try:
            delivery.current_latitude = float(latitude)
            delivery.current_longitude = float(longitude)
            delivery.save()
            return JsonResponse({
                'success': True,
                'message': 'Location updated successfully.',
                'current_latitude': float(delivery.current_latitude),
                'current_longitude': float(delivery.current_longitude),
            })
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid coordinates provided.'}, status=400)

    return JsonResponse({'error': 'Method not allowed.'}, status=405)


@role_required(['admin'])
def delivery_create(request):
    deliveries_with_order_ids = Delivery.objects.values_list('order_id', flat=True)
    orders = Order.objects.exclude(id__in=deliveries_with_order_ids).filter(
        status__in=[Order.STATUS_READY, Order.STATUS_OUT_FOR_DELIVERY]
    )
    drivers = User.objects.filter(role='driver')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        driver_id = request.POST.get('driver_id')
        status = request.POST.get('status')

        delivery = Delivery.objects.create(
            order_id=order_id,
            driver_id=driver_id if driver_id else None,
            status=status,
            current_latitude=request.POST.get('current_latitude') or None,
            current_longitude=request.POST.get('current_longitude') or None,
        )

        if delivery.status in [Delivery.STATUS_ASSIGNED, Delivery.STATUS_PICKED_UP, Delivery.STATUS_ON_THE_WAY]:
            delivery.order.status = Order.STATUS_OUT_FOR_DELIVERY
            delivery.order.save()

        if delivery.status == Delivery.STATUS_DELIVERED:
            delivery.order.status = Order.STATUS_DELIVERED
            delivery.order.save()

        # Create notification for customer about delivery assignment
        if delivery.driver:
            Notification.create_delivery_notification(
                user=delivery.order.customer,
                delivery=delivery,
                title="Delivery Assigned",
                message=f"Your order #{delivery.order.id} has been assigned to courier {delivery.driver.username}."
            )

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
        selectable_orders = Order.objects.exclude(id__in=deliveries_with_order_ids).filter(
            status__in=[Order.STATUS_READY, Order.STATUS_OUT_FOR_DELIVERY]
        )
        orders = (Order.objects.filter(id=delivery.order_id) | selectable_orders).distinct()
        drivers = User.objects.filter(role='driver')

        if request.method == 'POST':
            delivery.order_id = request.POST.get('order_id')
            driver_id = request.POST.get('driver_id')
            delivery.driver_id = driver_id if driver_id else None
            delivery.status = request.POST.get('status')
            delivery.current_latitude = request.POST.get('current_latitude') or None
            delivery.current_longitude = request.POST.get('current_longitude') or None
            delivery.save()

            if delivery.status in [Delivery.STATUS_ASSIGNED, Delivery.STATUS_PICKED_UP, Delivery.STATUS_ON_THE_WAY]:
                delivery.order.status = Order.STATUS_OUT_FOR_DELIVERY
                delivery.order.save()

            if delivery.status == Delivery.STATUS_DELIVERED:
                delivery.order.status = Order.STATUS_DELIVERED
                delivery.order.save()

            # Create notification for customer about delivery status change
            status_messages = {
                Delivery.STATUS_ASSIGNED: f"Your order #{delivery.order.id} has been assigned to a courier.",
                Delivery.STATUS_PICKED_UP: f"Your order #{delivery.order.id} has been picked up by the courier.",
                Delivery.STATUS_ON_THE_WAY: f"Your order #{delivery.order.id} is on the way to you.",
                Delivery.STATUS_DELIVERED: f"Your order #{delivery.order.id} has been delivered successfully.",
            }

            if delivery.status in status_messages:
                Notification.create_delivery_notification(
                    user=delivery.order.customer,
                    delivery=delivery,
                    title="Delivery Update",
                    message=status_messages[delivery.status]
                )

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
        delivery.current_latitude = request.POST.get('current_latitude') or delivery.current_latitude
        delivery.current_longitude = request.POST.get('current_longitude') or delivery.current_longitude
        delivery.save()

        if delivery.status in [Delivery.STATUS_PICKED_UP, Delivery.STATUS_ON_THE_WAY]:
            delivery.order.status = Order.STATUS_OUT_FOR_DELIVERY
            delivery.order.save()

        if delivery.status == Delivery.STATUS_DELIVERED:
            delivery.order.status = Order.STATUS_DELIVERED
            delivery.order.save()

        # Create notification for customer about delivery status change by driver
        status_messages = {
            Delivery.STATUS_PICKED_UP: f"Your order #{delivery.order.id} has been picked up by courier {delivery.driver.username}.",
            Delivery.STATUS_ON_THE_WAY: f"Your order #{delivery.order.id} is on the way to you.",
            Delivery.STATUS_DELIVERED: f"Your order #{delivery.order.id} has been delivered successfully.",
        }

        if delivery.status in status_messages:
            Notification.create_delivery_notification(
                user=delivery.order.customer,
                delivery=delivery,
                title="Delivery Update",
                message=status_messages[delivery.status]
            )

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


@role_required(['admin'])
def delivery_reassign_courier(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    drivers = User.objects.filter(role='driver')

    if request.method == 'POST':
        driver_id = request.POST.get('driver_id')
        delivery.driver_id = driver_id if driver_id else None
        delivery.save()

        # Create notification for customer about courier reassignment
        if delivery.driver:
            Notification.create_delivery_notification(
                user=delivery.order.customer,
                delivery=delivery,
                title="Courier Reassigned",
                message=f"The courier for your order #{delivery.order.id} has been changed to {delivery.driver.username}."
            )

        messages.success(request, f'Courier reassigned successfully for delivery #{delivery.id}.')
        return redirect('delivery_list')

    return render(request, 'delivery/delivery_reassign_courier.html', {
        'delivery': delivery,
        'drivers': drivers,
    })


@role_required(['admin', 'manager', 'client', 'driver'])
def courier_info(request, pk):
    courier = get_object_or_404(User, pk=pk, role='driver')
    deliveries = Delivery.objects.filter(driver=courier).select_related(
        'order', 'order__customer', 'order__restaurant'
    ).order_by('-created_at')[:10]  # Last 10 deliveries

    # Statistics
    total_deliveries = Delivery.objects.filter(driver=courier).count()
    completed_deliveries = Delivery.objects.filter(driver=courier, status='delivered').count()
    active_deliveries = Delivery.objects.filter(driver=courier).exclude(status='delivered').count()

    return render(request, 'delivery/courier_info.html', {
        'courier': courier,
        'deliveries': deliveries,
        'total_deliveries': total_deliveries,
        'completed_deliveries': completed_deliveries,
        'active_deliveries': active_deliveries,
        'completion_rate': (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
    })