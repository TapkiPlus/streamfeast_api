from django.test import TestCase
from .models import *
from .platron_client import *

# Create your tests here.
class PlatronTestCase(TestCase):

    def setUp(self):
        tt1 = TicketType.objects.create(price = 42)
        tt2 = TicketType.objects.create(price = 43)
        order = Order.objects.create(amount = 128)
        item = OrderItem.objects.create(order = order, ticket_type = tt1, quantity = 1, amount = 42)
        item = OrderItem.objects.create(order = order, ticket_type = tt2, quantity = 2, amount = 86)
        pass

    def test_platron_init_and_cancel(self): 
        txn = init_payment(Order.objects.first())
        txn.save()
        pers = PlatronPayment.objects.first()
        self.assertEqual(txn, pers)
        get_payment_status(txn.id)
        canc = cancel_payment(txn.id)
        get_payment_status(txn.id)
        
    def test_platron_cancel_and_mark(self): 
        pass
