from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages

from .models import MenuItem
from restaurants.models import Restaurant
from orders.models import OrderItem
from accounts.decorators import role_required


def menu_list(request):
    restaurant_id = request.GET.get('restaurant')
    query = request.GET.get('q', '').strip()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    selected_restaurant = None

    if request.user.is_authenticated:
        if request.user.role == 'admin':
            items = MenuItem.objects.select_related('restaurant').all()
            restaurants = Restaurant.objects.all()
        elif request.user.role == 'manager':
            items = MenuItem.objects.select_related('restaurant').filter(
                restaurant__manager=request.user
            )
            restaurants = Restaurant.objects.filter(manager=request.user)
        else:
            items = MenuItem.objects.select_related('restaurant').all()
            restaurants = Restaurant.objects.all()
    else:
        items = MenuItem.objects.select_related('restaurant').all()
        restaurants = Restaurant.objects.all()

    if restaurant_id:
        selected_restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        items = items.filter(restaurant_id=restaurant_id)

    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(restaurant__name__icontains=query)
        )

    context = {
        'items': items,
        'restaurants': restaurants,
        'selected_restaurant': selected_restaurant,
        'query': query,
        'restaurant_id': restaurant_id,
    }

    if is_ajax:
        return render(request, 'menu/partials/menu_results.html', context)

    return render(request, 'menu/menu_list.html', context)


@role_required(['admin', 'manager'])
def menu_create(request):
    restaurants = Restaurant.objects.all() if request.user.role == 'admin' else Restaurant.objects.filter(manager=request.user)

    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        price = request.POST.get('price')

        try:
            price_value = float(price)
            if price_value <= 0:
                messages.error(request, 'Price must be greater than 0.')
                return redirect('menu_create')
        except (TypeError, ValueError):
            messages.error(request, 'Invalid price.')
            return redirect('menu_create')

        if request.user.role == 'manager':
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, manager=request.user)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        MenuItem.objects.create(
            restaurant=restaurant,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            image_url=request.POST.get('image_url'),
            category=request.POST.get('category') or 'other',
            price=price,
            is_available=bool(request.POST.get('is_available'))
        )

        messages.success(request, 'Menu item created successfully.')
        return redirect('menu_list')

    return render(request, 'menu/menu_form.html', {
        'restaurants': restaurants,
        'category_choices': MenuItem.CATEGORY_CHOICES,
    })


@role_required(['admin', 'manager'])
def menu_update(request, pk):
    if request.user.role == 'admin':
        item = get_object_or_404(MenuItem, pk=pk)
        restaurants = Restaurant.objects.all()
    else:
        item = get_object_or_404(MenuItem, pk=pk, restaurant__manager=request.user)
        restaurants = Restaurant.objects.filter(manager=request.user)

    if request.method == 'POST':
        price = request.POST.get('price')

        try:
            price_value = float(price)
            if price_value <= 0:
                messages.error(request, 'Price must be greater than 0.')
                return redirect('menu_update', pk=item.pk)
        except (TypeError, ValueError):
            messages.error(request, 'Invalid price.')
            return redirect('menu_update', pk=item.pk)

        restaurant_id = request.POST.get('restaurant_id')

        if request.user.role == 'manager':
            restaurant = get_object_or_404(Restaurant, id=restaurant_id, manager=request.user)
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        item.restaurant = restaurant
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.image_url = request.POST.get('image_url')
        item.category = request.POST.get('category') or 'other'
        item.price = price
        item.is_available = bool(request.POST.get('is_available'))
        item.save()

        messages.success(request, 'Menu item updated successfully.')
        return redirect('menu_list')

    return render(request, 'menu/menu_form.html', {
        'item': item,
        'restaurants': restaurants,
        'category_choices': MenuItem.CATEGORY_CHOICES,
    })


@role_required(['admin'])
def menu_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)

    if OrderItem.objects.filter(menu_item=item).exists():
        messages.error(request, 'This item cannot be deleted because it already exists in an order.')
        return redirect('menu_list')

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted successfully.')
        return redirect('menu_list')

    return render(request, 'menu/menu_confirm_delete.html', {'item': item})