from .models import Cart


def cart_item_count(request):
    count = 0

    if request.user.is_authenticated and getattr(request.user, 'role', None) == 'client':
        cart = Cart.objects.filter(customer=request.user).first()

        if cart:
            count = sum(item.quantity for item in cart.items.all())

    return {
        'cart_item_count': count
    }