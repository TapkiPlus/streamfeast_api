from .models import Cart, CartItem


def check_if_cart_exists(session_id):
    cart, created = Cart.objects.get_or_create(session=session_id)
    return cart


def calculate_cart_price(cart):
    items = CartItem.objects.filter(parent=cart)
    price = 0
    for i in items:
        price += i.quantity * i.ticket_type.price
    cart.total_price = price
    cart.save()


def clear_cart(cart):
    cart.total_price = 0
    cart.save()
    items = CartItem.objects.filter(parent=cart).delete()
