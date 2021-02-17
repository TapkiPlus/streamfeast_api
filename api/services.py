from .models import Cart


def check_if_cart_exists(session_id):
    cart, created = Cart.objects.get_or_create(session=session_id)
    if created:
        print('new cart created')
    else:
        print('cart already created')
    return cart


def calculate_cart_price(cart):
    items = cart.tickets.all()
    price = 0
    for i in items:
        price += i.quantity * i.ticket.price
    cart.total_price = price
    cart.save()

def clear_cart(cart):
    items = cart.tickets.all()
    for i in items:
        i.delete()