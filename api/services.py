from .models import Cart


def check_if_cart_exists(session_id):
    cart, created = Cart.objects.get_or_create(session=session_id)
    if created:
        print('new cart created')
    else:
        print('cart already created')
    return cart


def add_to_cart(item, session_id):
    cart = check_if_cart_exists(session_id)
