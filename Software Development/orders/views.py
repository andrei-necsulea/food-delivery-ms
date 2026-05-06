from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Order, Cart, CartItem, OrderItem
from menu.models import MenuItem
from accounts.models import User
from restaurants.models import Restaurant
from accounts.decorators import role_required
from notifications.models import Notification


@role_required(['admin', 'manager', 'client', 'driver'])
def order_list(request):
    if request.user.role == 'admin':
        orders = Order.objects.select_related(
            'customer', 'restaurant'
        ).prefetch_related(
            'items', 'items__menu_item'
        ).all()

    elif request.user.role == 'client':
        orders = Order.objects.select_related(
            'customer', 'restaurant'
        ).prefetch_related(
            'items', 'items__menu_item'
        ).filter(customer=request.user)

    elif request.user.role == 'manager':
        orders = Order.objects.select_related(
            'customer', 'restaurant'
        ).prefetch_related(
            'items', 'items__menu_item'
        ).filter(restaurant__manager=request.user)

    elif request.user.role == 'driver':
        orders = Order.objects.select_related(
            'customer', 'restaurant'
        ).prefetch_related(
            'items', 'items__menu_item'
        ).filter(delivery__driver=request.user)

    else:
        orders = Order.objects.none()

    return render(request, 'orders/order_list.html', {'orders': orders})


@role_required(['admin', 'manager', 'client'])
def order_update(request, pk):
    if request.user.role == 'admin':
        order = get_object_or_404(Order, pk=pk)
        customers = User.objects.filter(role='client')
        restaurants = Restaurant.objects.all()

        if request.method == 'POST':
            order.customer_id = request.POST.get('customer_id')
            order.restaurant_id = request.POST.get('restaurant_id')
            order.total_price = request.POST.get('total_price')
            order.status = request.POST.get('status')
            order.delivery_address = request.POST.get('delivery_address', '').strip()
            order.phone_number = request.POST.get('phone_number', '').strip()
            order.payment_method = request.POST.get('payment_method', Order.PAYMENT_METHOD_CASH)
            order.save()

            messages.success(request, 'Order updated successfully.')
            return redirect('order_list')

        return render(request, 'orders/order_form.html', {
            'order': order,
            'customers': customers,
            'restaurants': restaurants,
            'admin_mode': True,
            'manager_mode': False,
            'payment_methods': [choice[0] for choice in Order.PAYMENT_METHOD_CHOICES],
            'allowed_statuses': [choice[0] for choice in Order.STATUS_CHOICES],
        })

    if request.user.role == 'client':
        order = get_object_or_404(Order, pk=pk, customer=request.user)

        if order.status != Order.STATUS_CREATED:
            messages.error(request, 'You can only modify an order while it is still in created status.')
            return HttpResponseForbidden('You can only modify an order while it is still in created status.')

        if request.method == 'POST':
            # Only allow payment method to be changed - address and phone cannot be modified after checkout
            order.payment_method = request.POST.get('payment_method', Order.PAYMENT_METHOD_CASH)
            order.save()

            # Create notification for customer about order modification
            Notification.create_order_notification(
                user=order.customer,
                order=order,
                title="Order Modified",
                message=f"Your order #{order.id} has been successfully modified."
            )

            messages.success(request, 'Order updated successfully.')
            return redirect('order_list')

        return render(request, 'orders/order_form.html', {
            'order': order,
            'client_mode': True,
            'manager_mode': False,
            'client_readonly_mode': True,
            'payment_methods': [choice[0] for choice in Order.PAYMENT_METHOD_CHOICES],
        })

    order = get_object_or_404(Order, pk=pk, restaurant__manager=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed_statuses = order.get_allowed_next_statuses_for_manager()

        if new_status not in allowed_statuses:
            messages.error(request, 'Invalid status transition for manager.')
            return HttpResponseForbidden("Invalid status transition for manager.")

        order.status = new_status
        order.save()

        # Create notification for customer about status change
        status_messages = {
            Order.STATUS_ACCEPTED: f"Your order #{order.id} has been accepted by the restaurant.",
            Order.STATUS_PREPARING: f"Your order #{order.id} is now being prepared.",
            Order.STATUS_READY: f"Your order #{order.id} is ready for delivery.",
            Order.STATUS_OUT_FOR_DELIVERY: f"Your order #{order.id} is out for delivery.",
            Order.STATUS_DELIVERED: f"Your order #{order.id} has been delivered successfully.",
            Order.STATUS_CANCELLED: f"Your order #{order.id} has been cancelled.",
        }

        if new_status in status_messages:
            Notification.create_order_notification(
                user=order.customer,
                order=order,
                title="Order Status Update",
                message=status_messages[new_status]
            )

        messages.success(request, 'Order status updated successfully.')
        return redirect('order_list')

    return render(request, 'orders/order_form.html', {
        'order': order,
        'manager_mode': True,
        'allowed_statuses': order.get_allowed_next_statuses_for_manager(),
    })


@role_required(['client'])
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)

    if order.status != Order.STATUS_CREATED:
        messages.error(request, "You can only cancel orders that are still in 'created' status.")
        return HttpResponseForbidden("You can only cancel orders that are still in 'created' status.")

    if request.method == 'POST':
        order.status = Order.STATUS_CANCELLED
        order.save()
        messages.success(request, 'Order cancelled successfully.')
        return redirect('order_list')

    return render(request, 'orders/order_confirm_cancel.html', {'order': order})


@role_required(['admin'])
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully.')
        return redirect('order_list')

    return render(request, 'orders/order_confirm_delete.html', {'order': order})


@role_required(['client'])
def add_to_cart(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, pk=menu_item_id)

    if not menu_item.is_available:
        messages.error(request, 'This item is currently unavailable.')
        return redirect('menu_list')

    cart, created = Cart.objects.get_or_create(customer=request.user)

    if cart.restaurant and cart.restaurant != menu_item.restaurant:
        messages.error(
            request,
            'You can only order from one restaurant at a time. Please clear your current cart first.'
        )
        return redirect('cart_detail')

    if not cart.restaurant:
        cart.restaurant = menu_item.restaurant
        cart.save()

    cart_item = CartItem.objects.filter(cart=cart, menu_item=menu_item).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        CartItem.objects.create(cart=cart, menu_item=menu_item, quantity=1)

    messages.success(request, f'{menu_item.name} added to cart.')
    return redirect('cart_detail')

    if not cart.restaurant:
        cart.restaurant = menu_item.restaurant
        cart.save()

    cart_item = CartItem.objects.filter(cart=cart, menu_item=menu_item).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        CartItem.objects.create(cart=cart, menu_item=menu_item, quantity=1)

    messages.success(request, f'{menu_item.name} added to cart.')
    return redirect('cart_detail')


@role_required(['client'])
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.select_related('menu_item', 'menu_item__restaurant').all()

    return render(request, 'orders/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart.total_price(),
    })


@role_required(['client'])
def update_cart_item(request, item_id):
    cart = get_object_or_404(Cart, customer=request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            item.delete()
            messages.success(request, 'Item removed from cart.')
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, 'Cart updated successfully.')

    return redirect('cart_detail')


@role_required(['client'])
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, customer=request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    if request.method == 'POST':
        item.delete()

        if not cart.items.exists():
            cart.restaurant = None
            cart.save()

        messages.success(request, 'Item removed from cart.')

    return redirect('cart_detail')


@role_required(['client'])
def clear_cart(request):
    cart = get_object_or_404(Cart, customer=request.user)

    if request.method == 'POST':
        cart.items.all().delete()
        cart.restaurant = None
        cart.save()

        messages.success(request, 'Cart cleared successfully.')

    return redirect('cart_detail')


@role_required(['client'])
def delivery_details(request):
    cart = get_object_or_404(Cart, customer=request.user)
    cart_items = cart.items.select_related('menu_item').all()

    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_detail')

    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if not delivery_address:
            messages.error(request, 'Delivery address is required.')
            return render(request, 'orders/delivery_details.html', {
                'cart': cart,
                'cart_items': cart_items,
                'cart_total': cart.total_price(),
                'delivery_address': delivery_address,
                'phone_number': phone_number,
            })

        if not phone_number:
            messages.error(request, 'Phone number is required.')
            return render(request, 'orders/delivery_details.html', {
                'cart': cart,
                'cart_items': cart_items,
                'cart_total': cart.total_price(),
                'delivery_address': delivery_address,
                'phone_number': phone_number,
            })

        # Store delivery details in session
        request.session['delivery_address'] = delivery_address
        request.session['phone_number'] = phone_number
        request.session.modified = True

        return redirect('checkout')

    return render(request, 'orders/delivery_details.html', {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart.total_price(),
        'delivery_address': request.user.address or '',
        'phone_number': request.user.phone_number or '',
    })


@role_required(['client'])
def checkout(request):
    cart = get_object_or_404(Cart, customer=request.user)
    cart_items = cart.items.select_related('menu_item').all()

    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_detail')

    # Get delivery details from session
    delivery_address = request.session.get('delivery_address', '')
    phone_number = request.session.get('phone_number', '')

    if not delivery_address or not phone_number:
        messages.error(request, 'Please provide delivery details before checkout.')
        return redirect('delivery_details')

    order = Order.objects.create(
        customer=request.user,
        restaurant=cart.restaurant,
        total_price=cart.total_price(),
        status=Order.STATUS_CREATED,
        delivery_address=delivery_address,
        phone_number=phone_number,
        payment_method=Order.PAYMENT_METHOD_CASH,
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            menu_item=item.menu_item,
            quantity=item.quantity,
            price_at_order_time=item.menu_item.price
        )

    cart.items.all().delete()
    cart.restaurant = None
    cart.save()

    # Clear delivery details from session
    if 'delivery_address' in request.session:
        del request.session['delivery_address']
    if 'phone_number' in request.session:
        del request.session['phone_number']
    request.session.modified = True

    # Create notification for customer about new order
    Notification.create_order_notification(
        user=request.user,
        order=order,
        title="Order Placed Successfully",
        message=f"Your order #{order.id} has been placed successfully. Total: {order.total_price} lei."
    )

    messages.success(request, 'Order placed successfully.')
    return redirect('order_list')