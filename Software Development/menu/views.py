from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import MenuItem
from restaurants.models import Restaurant
from accounts.decorators import role_required


def menu_list(request):
    restaurant_id = request.GET.get('restaurant')
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

    return render(request, 'menu/menu_list.html', {
        'items': items,
        'restaurants': restaurants,
        'selected_restaurant': selected_restaurant,
    })


@role_required(['admin', 'manager'])
def menu_create(request):
    if request.user.role == 'admin':
        restaurants = Restaurant.objects.all()
    else:
        restaurants = Restaurant.objects.filter(manager=request.user)

    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        price = request.POST.get('price')

        if request.user.role == 'manager':
            restaurant = get_object_or_404(
                Restaurant,
                id=restaurant_id,
                manager=request.user
            )
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        MenuItem.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            image_url=image_url,
            price=price
        )

        messages.success(request, 'Menu item created successfully.')
        return redirect('menu_list')

    return render(request, 'menu/menu_form.html', {
        'restaurants': restaurants
    })


@role_required(['admin', 'manager'])
def menu_update(request, pk):
    if request.user.role == 'admin':
        item = get_object_or_404(MenuItem, pk=pk)
        restaurants = Restaurant.objects.all()
    else:
        item = get_object_or_404(
            MenuItem,
            pk=pk,
            restaurant__manager=request.user
        )
        restaurants = Restaurant.objects.filter(manager=request.user)

    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        price = request.POST.get('price')

        if request.user.role == 'manager':
            restaurant = get_object_or_404(
                Restaurant,
                id=restaurant_id,
                manager=request.user
            )
        else:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        item.restaurant = restaurant
        item.name = name
        item.description = description
        item.image_url = image_url
        item.price = price
        item.save()

        messages.success(request, 'Menu item updated successfully.')
        return redirect('menu_list')

    return render(request, 'menu/menu_form.html', {
        'item': item,
        'restaurants': restaurants
    })


@role_required(['admin'])
def menu_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted successfully.')
        return redirect('menu_list')

    return render(request, 'menu/menu_confirm_delete.html', {
        'item': item
    })