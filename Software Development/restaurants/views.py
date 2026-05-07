from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Prefetch
from django.contrib import messages
from .models import Restaurant, WorkingHours
from menu.models import MenuItem
from orders.models import OrderItem
from accounts.decorators import role_required


def restaurant_list(request):
    query = request.GET.get('q', '').strip()
    cuisine = request.GET.get('cuisine', '').strip()
    location = request.GET.get('location', '').strip()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

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
            Q(menu_items__name__icontains=query) |
            Q(menu_items__category__icontains=query)
        ).distinct()

    # Filter by cuisine exact match (from dropdown) and by address/location substring
    if cuisine:
        restaurants = restaurants.filter(cuisine_type__iexact=cuisine)

    if location:
        restaurants = restaurants.filter(address__icontains=location)

    context = {
        'restaurants': restaurants,
        'query': query,
        'cuisine': cuisine,
        'location': location,
    }

    # Provide cuisine options for the filter select
    cuisine_qs = Restaurant.objects.values_list('cuisine_type', flat=True).distinct().order_by('cuisine_type')
    cuisine_choices = [c for c in cuisine_qs if c]
    context['cuisine_choices'] = cuisine_choices

    if is_ajax:
        return render(request, 'restaurants/partials/restaurant_results.html', context)

    return render(request, 'restaurants/restaurant_list.html', context)

def restaurant_detail(request, pk):
    if request.user.is_authenticated and request.user.role == 'manager':
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)
    else:
        restaurant = get_object_or_404(Restaurant, pk=pk)

    menu_items = restaurant.menu_items.all()

    return render(request, 'restaurants/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })


@role_required(['admin', 'manager'])
def restaurant_create(request):
    if request.method == 'POST':
        manager_id = request.POST.get('manager_id') if request.user.role == 'admin' else request.user.id

        Restaurant.objects.create(
            name=request.POST.get('name'),
            address=request.POST.get('address'),
            cuisine_type=request.POST.get('cuisine_type'),
            description=request.POST.get('description'),
            image_url=request.POST.get('image_url'),
            rating=request.POST.get('rating') or 4.5,
            delivery_time=request.POST.get('delivery_time') or "30-45 min",
            working_hours=request.POST.get('working_hours') or "10:00 - 22:00",
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
        restaurant.working_hours = request.POST.get('working_hours') or "10:00 - 22:00"

        if request.user.role == 'admin':
            restaurant.manager_id = request.POST.get('manager_id')

        restaurant.save()
        messages.success(request, 'Restaurant updated successfully.')
        return redirect('restaurant_list')

    return render(request, 'restaurants/restaurant_form.html', {'restaurant': restaurant})


@role_required(['admin', 'manager'])
def restaurant_delete(request, pk):
    if request.user.role == 'admin':
        restaurant = get_object_or_404(Restaurant, pk=pk)
    else:
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)

    # Check if there are any orders with items from this restaurant
    menu_items = restaurant.menu_items.all()
    if OrderItem.objects.filter(menu_item__in=menu_items).exists():
        messages.error(request, 'This restaurant cannot be deleted because it has items in existing orders.')
        return redirect('restaurant_list')

    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Restaurant deleted successfully.')
        return redirect('restaurant_list')

    return render(request, 'restaurants/restaurant_confirm_delete.html', {'restaurant': restaurant})


@role_required(['admin', 'manager'])
def working_hours_edit(request, pk):
    """Edit working hours for a restaurant (manager or admin only)"""
    if request.user.role == 'admin':
        restaurant = get_object_or_404(Restaurant, pk=pk)
    else:
        restaurant = get_object_or_404(Restaurant, pk=pk, manager=request.user)

    # Ensure all 7 days have entries
    for day in range(7):
        WorkingHours.objects.get_or_create(
            restaurant=restaurant,
            day_of_week=day,
            defaults={'opening_time': '09:00', 'closing_time': '21:00'}
        )

    working_hours = restaurant.working_hour_entries.all().order_by('day_of_week')

    if request.method == 'POST':
        day_dict = dict(WorkingHours.DAYS_OF_WEEK)
        
        for working_hour in working_hours:
            day_num = working_hour.day_of_week
            is_closed = request.POST.get(f'day_{day_num}_closed') == 'on'
            
            if is_closed:
                working_hour.is_closed = True
            else:
                opening_time = request.POST.get(f'day_{day_num}_opening')
                closing_time = request.POST.get(f'day_{day_num}_closing')
                
                if opening_time and closing_time:
                    if opening_time >= closing_time:
                        messages.error(request, f'{day_dict[day_num]}: Opening time must be before closing time.')
                        break
                    working_hour.opening_time = opening_time
                    working_hour.closing_time = closing_time
                    working_hour.is_closed = False
            
            working_hour.save()
        else:
            messages.success(request, 'Working hours updated successfully.')
            return redirect('restaurant_list')

    return render(request, 'restaurants/working_hours.html', {
        'restaurant': restaurant,
        'working_hours': working_hours,
    })