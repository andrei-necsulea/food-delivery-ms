from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Prefetch
from django.contrib import messages
from .models import Restaurant
from menu.models import MenuItem
from accounts.decorators import role_required


def restaurant_list(request):
    query = request.GET.get('q', '').strip()

    base_queryset = Restaurant.objects.prefetch_related(
        Prefetch('menu_items', queryset=MenuItem.objects.all())
    )

    if request.user.is_authenticated:
        if request.user.role == 'admin':
            restaurants = base_queryset.all()
        elif request.user.role == 'manager':
            restaurants = base_queryset.filter(manager=request.user)
        else:
            restaurants = base_queryset.all()
    else:
        restaurants = base_queryset.all()

    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) |
            Q(cuisine_type__icontains=query) |
            Q(menu_items__name__icontains=query)
        ).distinct()

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants,
        'query': query,
    })


@role_required(['admin', 'manager'])
def restaurant_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        cuisine_type = request.POST.get('cuisine_type')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        rating = request.POST.get('rating') or 4.5
        delivery_time = request.POST.get('delivery_time') or "30-45 min"

        manager_id = request.POST.get('manager_id') if request.user.role == 'admin' else request.user.id

        Restaurant.objects.create(
            name=name,
            address=address,
            cuisine_type=cuisine_type,
            description=description,
            image_url=image_url,
            rating=rating,
            delivery_time=delivery_time,
            manager_id=manager_id
        )

        messages.success(request, 'Restaurant created successfully.')
        return redirect('restaurant_list')

    return render(request, 'restaurants/restaurant_form.html')


@role_required(['admin', 'manager'])
def restaurant_update(request, pk):
    if request.user.role == 'admin':
        restaurant = get_object_or_404(Restaurant, pk=pk)
    else:
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)

    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.address = request.POST.get('address')
        restaurant.cuisine_type = request.POST.get('cuisine_type')
        restaurant.description = request.POST.get('description')
        restaurant.image_url = request.POST.get('image_url')
        restaurant.rating = request.POST.get('rating') or 4.5
        restaurant.delivery_time = request.POST.get('delivery_time') or "30-45 min"

        if request.user.role == 'admin':
            restaurant.manager_id = request.POST.get('manager_id')

        restaurant.save()
        messages.success(request, 'Restaurant updated successfully.')
        return redirect('restaurant_list')

    return render(request, 'restaurants/restaurant_form.html', {'restaurant': restaurant})


@role_required(['admin'])
def restaurant_delete(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)

    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Restaurant deleted successfully.')
        return redirect('restaurant_list')

    return render(request, 'restaurants/restaurant_confirm_delete.html', {'restaurant': restaurant})